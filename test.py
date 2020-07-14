import asyncio
import random
import time
import aiohttp
import async_timeout

class Myclass:
    def __init__(self, url):
        self.queue = asyncio.Queue(300)
        self.url = url
        self.session = aiohttp.ClientSession()

    async def worker(self, name, queue):
        while True:
            # Get a "work item" out of the queue.
            sleep_for = await queue.get()
            with async_timeout.timeout(2):
                async with self.session.post(self.url, data={"test": sleep_for}) as request:
                    response = await request.text()
                    print(response)
            # Notify the queue that the "work item" has been processed.
            queue.task_done()

            print(f'{name} has slept for {sleep_for:.2f} seconds')

    def put_in_queue(self, sleep_for):
        self.queue.put_nowait(sleep_for)

    async def main(self):

        # Generate random timings and put them into the queue.
        total_sleep_time = 0
        self.put_in_queue(10)
        # Create three worker tasks to process the queue concurrently.
        tasks = []
        loop = asyncio.get_event_loop()
        for i in range(1):
            task = loop.create_task(self.worker(f'worker-{i}', self.queue))
            tasks.append(task)

        # Wait until the queue is fully processed.
        started_at = time.monotonic()
        await self.queue.join()
        total_slept_for = time.monotonic() - started_at

        # Cancel our worker tasks.
        for task in tasks:
            task.cancel()
        await self.session.close()
        print('====')
        print(f'3 workers slept in parallel for {total_slept_for:.2f} seconds')
        print(f'total expected sleep time: {total_sleep_time:.2f} seconds')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    n = Myclass(url='http://192.168.11.22:7480/gain/echo/d84f4212-c53f-451f-927e-77edb22f50ee')
    n.put_in_queue(2)
    n.put_in_queue(1)
    n.put_in_queue(1.5)
    n.put_in_queue(7)
    coro = loop.create_task(n.main())
    loop.run_until_complete(coro)
    loop.close()