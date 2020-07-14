import asyncio
from loguru import logger
import sys
import aiohttp
import async_timeout


from config import QUEUE_MAX_SIZE, LOG_LEVEL

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level=LOG_LEVEL)



class NetworkSenderError(Exception):
    pass


class NetworkSender:

    headers = {'Content-Type': 'application/json'}

    def __init__(self, url):
        self.queue = asyncio.Queue(QUEUE_MAX_SIZE)
        self.url = url
        self.session = aiohttp.ClientSession(raise_for_status=True,
                                             conn_timeout=3,
                                             headers=self.headers
                                             )

    async def worker(self, name, queue):
        while True:
            # Get a "work item" out of the queue.
            event = await queue.get()
            try:
                with async_timeout.timeout(2):
                    async with self.session.post(self.url, data=event.to_json()) as request:
                        response = await request.text()
                        logger.debug('Got response from endpoint {response}', response=response)
            except AttributeError:
                pass
            except Exception as err:
                logger.error('Cannot connect to the endpoint, timeout exceeded')
            # Notify the queue that the "work item" has been processed.
            # queue.task_done()

    async def close(self):
        await self.session.close()

    def put_in_queue(self, event):
        self.queue.put_nowait(event)

    def shutdown(self, loop):
        all_tasks = asyncio.Task.all_tasks(loop)
        for task in all_tasks:
            task.cancel()
        loop.run_until_complete((asyncio.gather(*all_tasks, loop=loop, return_exceptions=True)))
        for task in all_tasks:
            if task.cancelled():
                continue
            if task.exception() is not None:
                logger.warning('Coroutine error occurred')
        loop.run_until_complete(self.close())


    async def main(self, workers=1):

        # Create workers tasks to process the queue concurrently.
        tasks = []
        loop = asyncio.get_event_loop()

        for i in range(workers):
            task = loop.create_task(self.worker(f'worker-{i}', self.queue))
            tasks.append(task)

        while True:
            await asyncio.sleep(0.1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    n = NetworkSender(url='http://192.168.1.2:3456/endpoint/echo/d84f4212-c53f-451f-927e-77edb22f50ee')
    coro = loop.create_task(n.main())
    try:
        loop.run_until_complete(coro)
    except KeyboardInterrupt as err:
        n.shutdown(loop)


