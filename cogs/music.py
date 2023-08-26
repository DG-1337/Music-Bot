import discord
import settings
from discord.ext import commands 
import wavelink

logger = settings.logging.getLogger(__name__)

class MusicBot(commands.Cog):

    vc : wavelink.Player = None
    node: wavelink.Node = None
    track = None

    def __init__(self, bot):
        self.bot = bot

    # used to connect to lavalink
    async def setup(self):
        self.node = wavelink.Node(uri='http://localhost:2333', password='changeme')
        await wavelink.NodePool.connect(client=self.bot, nodes=[self.node])

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        logger.info(f"[{node}] is ready")

    @commands.hybrid_command(brief="Joins user's voice channel")
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        self.music_channel = ctx.message.channel
        if not channel:
            await ctx.send(f"You need to join a voice channel first.")
            return 
        self.vc = await channel.connect(cls=wavelink.Player)
        await ctx.send(f"Joined {channel}", ephemeral=True)

    @commands.hybrid_command(name="play", description="Plays vid")
    async def play(self, ctx, *, title : str):
        # checks if bot is in a vc if not executes join command
        bot_vc = discord.utils.get(self.bot.voice_clients, guild = ctx.guild)
        if bot_vc == None:
            await ctx.invoke(self.bot.get_command("join"))
        chosen_track = await wavelink.YouTubeTrack.search(title, return_first=True)

        if chosen_track != None:
            track = chosen_track
            await self.vc.play(chosen_track)
            await ctx.send(f"Now playing {chosen_track}", ephemeral=True)
            return

    @commands.hybrid_command(name="pause", desctription="Stops current track")
    async def pause(self, ctx):
        await self.vc.pause()
        await ctx.send(f"Paused Current track", ephemeral=True)

    # @commands.hybrid_command(name="skip", with_app_command=True)
    # async def skip(self, ctx):
    #     if self.vc.queue.is_empty:
    #         await ctx.send("Queue is empty")
    #         return
    #     self.track = self.vc.queue.get()
    #     await self.vc.play(self.track)

async def setup(bot):
    music_bot = MusicBot(bot)
    await bot.add_cog(music_bot)    
    await music_bot.setup()
