from .core import Bot
from .logger import Logger


logger = Logger(__name__)


if __name__ == "__main__":
    logger.INFO("Starting Bot")
    bot = Bot()
    bot.run()
