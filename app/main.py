import asyncio
from app.bot import MusicBot


async def main():
    """Main entry point for VTH Music Bot."""
    bot = MusicBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())

