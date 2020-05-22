import configparser
import pathlib
import sys
import traceback
from types import TracebackType

import discord
from discord.ext import commands

from .logger import Logger

logger = Logger(__name__)


class Bot(commands.Bot):
    def __init__(self) -> None:
        logger.INFO("reading config file")

        config_file_path = pathlib.Path("config.ini")
        if config_file_path.is_file():
            self.config = configparser.ConfigParser()
            self.config.read(config_file_path)
        else:
            logger.ERROR("config.ini not found")
            sys.exit()

        prefix = self.config["core"]["prefix"]
        super().__init__(command_prefix=prefix)

        self.server: discord.Guild = None

        # load cogs
        for cog in self.config["core"]["cogs"].split(","):
            self.load_extension(f"src.cogs.{cog}")

    def run(self) -> None:
        """
        Start the bot.
        """
        token = self.config["core"]["token"]
        super().run(token)

    def get_channel_from_config(self, channel_name: str) -> discord.TextChannel:
        channel_id = int(self.config["channels"][channel_name])
        return self.get_channel(channel_id)

    def get_role_from_config(self, role_name: str) -> discord.Role:
        role_id = int(self.config["roles"][role_name])
        return self.server.get_role(role_id)

    async def on_ready(self) -> None:
        logger.INFO(f"Logged in as {self.user.name}")

        status_channel = self.get_channel_from_config("status")
        embed = discord.Embed(color=discord.Color.green(), title="**Bot Online**")

        await status_channel.send(embed=embed)

        server_id = int(self.config["core"]["server"])
        self.server = self.get_guild(server_id)

    async def on_command(self, ctx: commands.Context) -> None:
        logger.INFO(f"command '{ctx.command.name}' activated by {ctx.author.name}")

    async def post_error(self, error_string: str, error_type: type, error: Exception, tb: TracebackType) -> None:
        bot_coder_role = self.get_role_from_config("bot_coder")
        error_channel = self.get_channel_from_config("error")

        tb_string = "\n".join(traceback.format_exception(error_type, error, tb))
        embed = discord.Embed(
                color=discord.Color.red(),
                title=error_string,
                )

        await error_channel.send(bot_coder_role.mention, embed=embed)
        await error_channel.send(f"```\n{tb_string}```")

    async def on_error(self, event: str, *args, **kwargs) -> None:  # type: ignore
        error_type, error, tb = sys.exc_info()

        # yes mypy I know that sys.exc_info() might return None, but it wont in this context :/
        error_string = f"{error_type.__name__} in {event}, {error}"  # type: ignore
        logger.ERROR(error_string)

        # again mypy they are not None
        await self.post_error(error_string, error_type, error, tb)  # type: ignore

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            logger.USER_ERROR(f"Could not find command: {error}")
            await ctx.send(f"Command not found :/, what are you trying to do?!\n{error}")
        elif isinstance(error, commands.BadArgument):
            logger.USER_ERROR(f"bad arguments to command, {error}")
            await ctx.send(f"Your inputs are wrong:\n{error}")
        elif isinstance(error, commands.MissingRequiredArgument):
            logger.USER_ERROR(f"missing command arguments")
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.CheckFailure):
            logger.USER_ERROR(f"user {ctx.author.name} cant use command {ctx.command.name}")
            await ctx.send(f"You cant use this command.\nhow did you know this was a thing then?!\nARE YOU A SPY?????????")
        else:
            error_string = f"{type(error).__name__} in command {ctx.command.name}, {error}"
            logger.ERROR(error_string)

            user_embed = discord.Embed(
                    color=discord.Color.red(),
                    title=error_string,
                    description="You Broke something :/\ndevelopers have been informed about the issue in a secret channel :open_mouth:"
                    )
            await ctx.send(ctx.author.mention, embed=user_embed)

            error_type = type(error)
            tb = error.__traceback__
            await self.post_error(error_string, error_type, error, tb)
