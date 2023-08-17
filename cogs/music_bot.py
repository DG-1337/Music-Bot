import discord 
from discord.ext import commands 
import settings

logger = settings.logging.getLogger(__name__)

class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    music_bot = MusicBot(bot)
    await bot.add_cog(music_bot)