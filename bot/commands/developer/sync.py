import inspect
from discord.ext import commands

from models.internal import CogModel


class Sync(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    async def cog_load(self):
        for command in self.get_commands():
            if isinstance(command, commands.HybridCommand):
                self.client.cogStatus.cog_status_append(
                    CogModel(
                        commandName=command.name.capitalize(),
                        filePath=inspect.getfile(command.callback),
                        status=True,
                        error=None
                    )
                )

    @commands.hybrid_command(name="sync", help="Syncs the bot's commands with Discord.")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        try:
            synced = await self.client.tree.sync()
            await ctx.send(f"Synced {len(synced)} commands successfully.")
        except Exception as e:
            await ctx.send(f"An error occurred while syncing commands: {e}")

async def setup(client: commands.Bot):
    await client.add_cog(Sync(client))