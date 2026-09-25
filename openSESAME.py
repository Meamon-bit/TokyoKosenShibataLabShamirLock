import asyncio

from gomalock.sesame5 import Sesame5

MAC_ADDRESS = ""
SECRET_KEY = ""

async def openSESAME():
    print("開錠信号送信")
    async with Sesame5(MAC_ADDRESS, SECRET_KEY) as sesame5:
        await sesame5.unlock("gomalock")
    print("開錠")

async def closeSESAME():
    print("施錠信号送信")
    async with Sesame5(MAC_ADDRESS, SECRET_KEY) as sesame5:
        await sesame5.lock("gomalock")
    print("施錠")

if __name__ == "__main__":
    asyncio.run(openSESAME())
