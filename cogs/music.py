import discord
import settings
from discord.ext import commands 
import wavelink

logger = settings.logging.getLogger(__name__)

class MusicBot(commands.Cog):

    vc : wavelink.Player = None
    node: wavelink.Node = None

    def __init__(self, bot):
        self.bot = bot

    # used to connect to lavalink
    async def setup(self):
        self.node = wavelink.Node(uri='http://localhost:2333', password='changeme')
        await wavelink.NodePool.connect(client=self.bot, nodes=[self.node])

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        logger.info(f"[{node}] is ready")

    @commands.command(brief="Joins user's voice channel")
    async def join(self, ctx, player=wavelink.Player):
        channel = ctx.message.author.voice.channel
        self.music_channel = ctx.message.channel
        if not channel:
            await ctx.send(f"You need to join a voice channel first.")
            return 
        self.vc = await channel.connect(cls=player)
        await ctx.send(f"Joined {channel.name}")

    @commands.command(brief="Search for a track on YouTube")
    async def play(self, ctx, *, title : str):
        # checks if bot is in a vc if not executes join command
        bot_vc = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)
        if bot_vc == None:
            await ctx.invoke(self.bot.get_command("join"))
        chosen_track = await wavelink.YouTubeTrack.search(title, return_first=True)
        await self.vc.play(chosen_track)


async def setup(bot):
    music_bot = MusicBot(bot)
    await bot.add_cog(music_bot)    
    await music_bot.setup()
