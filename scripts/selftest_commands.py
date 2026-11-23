"""Dry-load all bot cogs and report command registration failures."""
import asyncio
import os
import sys
import discord
from discord.ext import commands

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import COGS


async def main():
    bot = commands.Bot(command_prefix="+", intents=discord.Intents.default(), help_command=None)
    failures = []
    for cog in COGS:
        try:
            await bot.load_extension(cog)
        except Exception as exc:
            failures.append((cog, type(exc).__name__, str(exc)))
    print("Slash commands:", len(bot.tree.get_commands()))
    print("Prefix commands:", len(list(bot.commands)))
    for cog, error_type, message in failures:
        print("LOAD_FAIL {}: {}: {}".format(cog, error_type, message))
    await bot.close()
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
