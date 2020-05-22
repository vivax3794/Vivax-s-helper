from discord.ext import commands

from ..logger import Logger, LOGS
from ..core import Bot


logger = Logger(__name__)


class LogCommands(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = Bot

    @commands.command(aliases=["l"])
    @commands.is_owner()
    async def log(self, ctx: commands.Context, ammount: int = 10) -> None:
        """
        Displays the latest logs from the bot.
        """
        logs_to_display = LOGS[-ammount:]
        log_string = "\n".join(map(str, logs_to_display))

        if len(log_string) >= 2000:
            await ctx.send("output to long, I wont send this :/")
        else:
            await ctx.send(f"```py\n{log_string}```")


def setup(bot: Bot) -> None:
    bot.add_cog(LogCommands(Bot))
    logger.INFO("LogCommands cog loaded")
