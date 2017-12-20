import asyncio


class AsyncPool:
    def __init__(self, limit):
        self.limit = limit
        self.tasks = []

    async def add_task(self, coroutine):
        self.tasks.append(coroutine)
        if len(self.tasks) > self.limit:
            await asyncio.wait(self.tasks)
            self.tasks.clear()

    async def wait(self):
        if self.tasks:
            await asyncio.wait(self.tasks)
            self.tasks.clear()