import discord
from discord.ext import commands
from discord import Forbidden
from bot.client import MiBotClient

class Ping(commands.Cog):
    def __init__(self, client : MiBotClient):
        self.client = client


    # +-----------------+
    # |  Ping Command   |
    # +-----------------+

    @commands.hybrid_command(
        name="ping",
        description="Ping command to check bot latency."
    )
    @commands.cooldown(5, 2, commands.BucketType.user)
    async def ping(self, ctx : commands.Context):
        
        latency = round(self.client.latency * 1000)
        await ctx.send(f"Pong! Latency: {latency}ms", ephemeral=True)


    # +-----------------+
    # |  Error Handler  |
    # +-----------------+

    @ping.error
    async def ping_error(self, ctx : commands.Context, error : commands.CommandError):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Error! Bad Argument, please input proper arguments!", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Error! You lack permission to execute this command!", ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Error! Bot is missing permissions to execute this command!", ephemeral=True)
        elif isinstance(error, discord.NotFound):
            await ctx.send("Error! The specified user was not found!", ephemeral=True)
        elif isinstance(error, Forbidden):
            await ctx.send("Error! Bot lacks the necessary permissions to execute this command!", ephemeral=True)



async def setup(client : MiBotClient):
    await client.add_cog(Ping(client))