import argparse
import asyncio
import struct
import time
import sys

from holder import Holder
from packet_parser import Chain
from async_networksender import NetworkSender
from utils import bytes2bits
from loguru import logger
from error import ERRORLEVEL

from config import LIDARS_PARAMS, LOG_LEVEL


error_level = ERRORLEVEL.NORMAL
logger.start(sys.stderr, format="{time} {level} {message}", filter="my_module", level=LOG_LEVEL)


class State:
    def __init__(self):
        self.__is_working = True

    def is_working(self):
        return self.__is_working

    def stop(self):
        self.__is_working = False


class LidarClient:
    def __init__(self, event_hold_time, cubit_server_endpoint):
        self.holder = Holder(event_hold_time)
        self.chain = Chain()
        self.state = State()
        self.sender = NetworkSender(url=cubit_server_endpoint)

        self.lidars_id = {lidar["source"]: lidar["source_name"] for lidar in LIDARS_PARAMS}

        self.t = int(time.time())

    async def packet_handler(self, reader, writer):
        addr, port = writer.get_extra_info('peername')
        client_name = self.lidars_id.get(addr, None)
        if not client_name:
            logger.warning('Unknown client {addr}:{port}', addr=addr, port=port)
            writer.close()
            return
        logger.info("Client with ip address {addr}:{port}/{client_name} has connected",
                    addr=addr,
                    port=port,
                    client_name=client_name
                    )
        while self.state.is_working():
            data = await reader.read(60)
            if not data:
                break
            timestamp = time.time()
            events = []
            connection_info = {
                "source_name": client_name,
                "port": port,
                "timestamp": timestamp,
                "holder": self.holder
            }

            try:
                decoded_bytes = struct.unpack('>60B', data)
                decoded_bits = bytes2bits(decoded_bytes)[10:]
                events = self.chain.handle(decoded_bits, events, connection_info)
            except ValueError:
                pass
            except struct.error as err:
                logger.error('Cannot parse packet from client {addr}:{port}, skip it.', addr=addr, port=port)
            else:
                logger.debug('Push all events to the queue')
                for event in events:
                    self.holder.add(event)
        logger.info("Client with ip address {addr}:{port}/{client_name} has disconnected",
                    addr=addr,
                    port=port,
                    client_name=client_name
                    )

    async def event_handler(self, waitsec=1):
        while True:
            events = self.holder.get_ready_events()
            for event in events:
                self.sender.put_in_queue(event)
            await asyncio.sleep(waitsec)

    def close(self, loop):
        self.state.stop()
        loop.run_until_complete(self.sender.close())
        all_tasks = asyncio.Task.all_tasks(loop)
        for task in all_tasks:
            task.cancel()
        features = asyncio.gather(*all_tasks, loop=loop, return_exceptions=True)
        loop.run_until_complete(features)
        for task in all_tasks:
            if task.cancelled():
                continue
            if task.exception() is not None:
                logger.warning('Coroutine error occurred')


async def shutdown(loop):
    logger.info(f"Received exit signal stop...")
    tasks = [t for t in asyncio.Task.all_tasks() if t is not
             asyncio.Task.current_task()]

    [task.cancel() for task in tasks]

    logger.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


def handle_exception(loop, context):
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    logger.info("Shutting down...")
    loop.create_task(shutdown(loop))

def main(address, port, event_hold_time, server_endpoint):

    server = LidarClient(event_hold_time, server_endpoint)
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    global error_level

    try:
        server_coro = loop.create_task(asyncio.start_server(server.packet_handler, address, port, loop=loop))
        event_handler = loop.create_task(server.event_handler())
        sender_coro = loop.create_task(server.sender.main())

        tasks = asyncio.gather(server_coro, event_handler, sender_coro)
        logger.info('Serving on {host}:{port}', host=address, port=port)
    except OSError as err:
        error_level = int(ERRORLEVEL.BIND_ERROR)
    except Exception as err:
        error_level = int(ERRORLEVEL.UNKNOWN_ERROR)
    else:
        logger.info('Started service on {host}:{port}', host=address, port=port)
        try:
            loop.run_until_complete(tasks)
        except KeyboardInterrupt:
            error_level = int(ERRORLEVEL.NORMAL)
        except OSError as err:
            error_level = int(ERRORLEVEL.BIND_ERROR)
        finally:
            loop.create_task(shutdown(loop))
            loop.run_forever()
            sys.exit(error_level)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sick agent')
    parser.add_argument('-a', '--address', help='service address', type=str, required=True)
    parser.add_argument('-p', '--port', help='service port', default=7455, type=int)
    parser.add_argument('-t', '--event-hold-time', help='Event hold time', default=10, type=int)
    parser.add_argument('-g', '--point', help='api endpoint', type=str, required=False)
    args = parser.parse_args()
    main(address=args.address,
         port=args.port,
         event_hold_time=args.event_hold_time,
         server_endpoint=args.cubit
         )