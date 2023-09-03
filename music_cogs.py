import discord 
from discord.ext import commands
import settings
import utils
    
logger = settings.logging.getLogger("bot")
    
def run():

    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents)
    # sync slash commands
    
    @bot.event 
    async def on_ready():
        await utils.load_videocmds(bot)
        await bot.load_extension("cogs.music")
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)}, command(s)")

    # loads, unloads, and reloads music.py file
    @bot.command()
    async def load(ctx, cog: str):
        await bot.load_extension(f"cogs.{cog.lower()}")
        await ctx.send("Success")
        
    @bot.command()
    async def unload(ctx, interaction: discord.Interaction, cog: str):
        await bot.unload_extension(f"cogs.{cog.lower()}")
        await ctx.send("Success")

    @bot.command()
    async def reload(ctx, cog: str):
        await bot.reload_extension(f"cogs.{cog.lower()}")
        await ctx.send("Success")

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)

if __name__ == "__main__":
    run()