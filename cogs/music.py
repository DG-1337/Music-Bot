import discord
import settings
from discord import Embed
from discord.ext import commands 
import wavelink

logger = settings.logging.getLogger(__name__)

class MusicBot(commands.Cog):

    # track = None

    def __init__(self, bot):
        self.bot = bot
        self.queue = wavelink.Queue()
        self.vc : wavelink.Player = None
        self.node: wavelink.Node = None
      

    # used to connect to lavalink
    async def setup(self):
        self.node = wavelink.Node(uri='http://localhost:2333', password='changeme')
        await wavelink.NodePool.connect(client=self.bot, nodes=[self.node])

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        logger.info(f"[{node}] is ready")
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload:wavelink.TrackEventPayload):
        await self.play_next_track()

    @commands.hybrid_command(brief="Joins user's voice channel")
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        self.music_channel = ctx.message.channel
        if not channel:
            await ctx.send(f"You need to join a voice channel first.")
            return 
        self.vc = await channel.connect(cls=wavelink.Player)
        await ctx.send(f"Joined {channel}", ephemeral=True)


    @commands.hybrid_command(name="p")
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        if not ctx.voice_client:
            self.vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            self.vc = ctx.voice_client
    
        tracks: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await ctx.send(f'It was not possible to find the song: `{search}`')
            return
    
        track: wavelink.YouTubeTrack = tracks[0]
        self.queue.put(track)
        self.music_channel = ctx.message.channel  # define music_channel here

        if not self.vc.is_playing():
            await self.play_next_track()
        else:
            await ctx.send(f"{track.title}, has been added")


    async def play_next_track(self):
        if not self.queue.is_empty:
            next_track = self.queue.get()
            await self.vc.play(next_track)
            await self.music_channel.send(f"{next_track}, has been added to the queue")
            

    @commands.hybrid_command(name="pause", desctription="Stops current track")
    async def pause(self, ctx):
        await self.vc.pause()
        await ctx.send(f"Paused Current track", ephemeral=True)

    @commands.hybrid_command(name="resume", desctription="Resumes current track")
    async def resume(self, ctx):
        await self.vc.resume()
        await ctx.send(f"Paused Current track", ephemeral=True)

    @commands.hybrid_command(name="disconnect", desctription="Disconnects bot from current vc")
    async def disconnect(self, ctx):
        await self.vc.disconnect()
        await ctx.send(f"Paused Current track", ephemeral=True)

    @commands.hybrid_command(name="skip")
    async def skip(self, ctx: commands.Context) -> None:
        vc: wavelink.Player = ctx.voice_client
        if not self.queue.is_empty:
            await vc.stop()
            next_track = self.queue.pop()
            await vc.play(next_track)
            ctx.send(f"Current song has been skipped")

        elif self.vc.is_playing() == True:
            await vc.stop()
            await ctx.send(f"Stopped current song")

async def setup(bot):
    music_bot = MusicBot(bot)
    await bot.add_cog(music_bot)    
    await music_bot.setup()
