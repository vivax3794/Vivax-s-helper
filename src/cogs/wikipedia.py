from typing import List
import textwrap

import discord
from discord.ext import commands
import aiohttp
import html2text
import EZPaginator

from ..logger import Logger
from ..core import Bot


logger = Logger(__name__)


SEARCH_API = "https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={}"
CONTENT_API = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&exintro=&titles={}"


class Wikipedia(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> any:  # type: ignore
        """
        Fetch the json from the given url.
        """
        async with session.get(url) as resp:
            return await resp.json()  # type: ignore

    async def get_titles(self, session: aiohttp.ClientSession, search: str) -> List[str]:
        """
        Get the titles of the wikipedia result.
        """
        logger.INFO(f"searching wikipedia for {search}")
        data = await self.fetch(session, SEARCH_API.format(search))
        titles: List[str] = []
        for page in data["query"]["search"]:  # type: ignore
            title: str = page["title"]
            titles.append(title)

        return titles

    async def get_page_contents(self, session: aiohttp.ClientSession, title: str) -> str:
        """
        Get the content of a wikipedia page.
        """
        logger.INFO(f"getting content for: {title}")
        data = await self.fetch(session, CONTENT_API.format(title))
        content: str = list(data["query"]["pages"].values())[0]["extract"]  # type: ignore
        content = html2text.html2text(content)
        content = textwrap.shorten(content, 2048, placeholder=" **...**")
        return content

    @commands.command(aliases=["wiki", "search", "w"])
    async def wikipedia(self, ctx: commands.Context, *, search: str) -> None:
        """
        Search the best source of information ever, WIKIPEDIA!
        """
        with ctx.typing():
            embeds = []
            async with aiohttp.ClientSession() as session:
                titles = await self.get_titles(session, search)
                logger.INFO(f"got {len(titles)} results.")
                for title in titles:
                    content = await self.get_page_contents(session, title)
                    embeds.append(discord.Embed(
                        color=discord.Color.blue(),
                        title=title,
                        description=content,
                        ))

        msg = await ctx.send(embed=embeds[0])
        paginator = EZPaginator.Paginator(self.bot, msg, embeds=embeds, timeout=30, use_more=True)
        logger.INFO("starting pagination of the results")
        await paginator.start()


def setup(bot: Bot) -> None:
    bot.add_cog(Wikipedia(bot))
    logger.INFO("Loaded Wikipedia cog.")
