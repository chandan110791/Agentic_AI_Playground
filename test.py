import logging

logging.basicConfig(level=logging.INFO,filename="abc.log")
logger = logging.getLogger(__name__)

import asyncio

async def main():
        testInput = input("hi")
        await display_result(testInput)

async def display_result(test:str):
      logger.info(f"input is {test}")
      print("bye")


if __name__== "__main__":
    asyncio.run(main())
