import discord
import re
from buttons import SimpleView
import settings
from discord import Embed
from discord.ext import commands 
import wavelink

logger = settings.logging.getLogger(__name__)


# commands for music bot 
class MusicBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.queue = wavelink.Queue()
        self.vc : wavelink.Player = None
        self.node: wavelink.Node = None
        self.track: wavelink.YouTubeTrack = None
      
    # used to connect to lavalink
    async def setup(self):
        self.node = wavelink.Node(uri='http://localhost:2333', password=settings.LAVA_LINK_PASSWORD)
        await wavelink.NodePool.connect(client=self.bot, nodes=[self.node])

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        logger.info(f"[{node}] is ready")
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload:wavelink.TrackEventPayload):
        await self.play_next_track()

    # if user isn't in channel then bot will not join the vc
    @commands.hybrid_command(brief="Joins user's voice channel")
    async def join(self, ctx):
        try:
            channel = ctx.message.author.voice.channel

        except AttributeError:
            await ctx.send(f"You need to be in a Voice Channel to use  the `play` command", ephemeral=True)

        else:
            self.music_channel = ctx.message.channel
            self.vc = await channel.connect(cls=wavelink.Player)
            await ctx.send(f"Joined {channel}", ephemeral=True)


    @commands.hybrid_command(name="play", brief="Plays songs from YouTube")
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        
        if not ctx.voice_client:
            await ctx.invoke(self.bot.get_command('join'))

        else:
            self.vc = ctx.voice_client

        self.track = await wavelink.YouTubeTrack.search(search, return_first=True)


        if not self.track:
            return await ctx.send(f'Could not find: `{search}`')
        
        self.queue.put(self.track)
        self.music_channel = ctx.message.channel 
        if not self.vc.is_playing():
            await self.play_next_track()

        else:
            await ctx.send(f"`{self.track}` has been added to the queue")

    async def play_next_track(self):
        if not self.queue.is_empty:
            next_track = self.queue.get()
            await self.vc.play(next_track)

            video_url = url= await self.track.fetch_thumbnail()
            embed = discord.Embed(title=f"`{self.track}` by `{self.track.author}`")
            embed.set_image(url=video_url)
            await self.music_channel.send(embed=embed)
          

    @commands.hybrid_command(name="pause", brief="Stops current track")
    async def pause(self, ctx):
        if self.vc.is_playing == False:
            return await self.music_channel(f"0 tracks are playing")
        await self.vc.pause()
        await ctx.send(f"Paused Current track", ephemeral=True)

    @commands.hybrid_command(name="resume", brief="Resumes current track")
    async def resume(self, ctx):
        if self.vc.is_playing == False:
            return await self.music_channel(f"0 tracks are playing")       
        await self.vc.resume()
        await ctx.send(f"Resumed Current track", ephemeral=True)

    @commands.hybrid_command(name="disconnect", brief="Disconnects from current VC")
    async def disconnect(self, ctx):
        await self.vc.disconnect()
        await ctx.send(f"Disconected", ephemeral=True)

    @commands.hybrid_command(name="skip", brief = "Skips current track")
    async def skip(self, ctx) -> None:
        vc: wavelink.Player = ctx.voice_client
        if not self.queue.is_empty:
            await vc.stop()
            next_track = self.queue.pop()
            await vc.play(next_track)
            await ctx.send(f"Current track has been skipped")

        elif self.vc.is_playing() == True:
            await vc.stop()
            await ctx.send(f"Stopped current tracl")

        else:
            await ctx.send("No track(s) is currently playing")

    async def button(self, ctx):
        view = SimpleView(timeout=50)
        message = await ctx.send(view=view)
        view.message = message
    

async def setup(bot):
    music_bot = MusicBot(bot)
    await bot.add_cog(music_bot)    
    await music_bot.setup()
