from typing import Literal
from discord.ext import commands
from bot.client import MiBotClient

from models.internal import CogModel
import inspect
import discord

from bot.modals.ticketModals import ModerationModal

class Ticket(commands.Cog):
    def __init__(self, client : MiBotClient):
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

    # +--------------------+
    # |   Ticket Command   |
    # +--------------------+

    @commands.hybrid_group(
        name="ticket",
        description="Open a ticket",
        with_app_command=True,
        fallback="add"
    )
    async def ticket(self, ctx : commands.Context, option: Literal["MODERATION", "BUG/GLITCH", "GENERAL"]):

        if ctx.interaction:
            await ctx.interaction.response.send_modal(ModerationModal())
        else:
            await ctx.send("This command can only be used via slash commands (/).", ephemeral=True)

    @ticket.command(
        name="remove",
        description="Close a ticket"
    )
    async def close_ticket(self, ctx : commands.Context):

        if ctx.interaction:
            await ctx.interaction.response.send_modal(ModerationModal())
        else:
            await ctx.send("This command can only be used via slash commands (/).", ephemeral=True)
        
async def setup(client: MiBotClient):
    await client.add_cog(Ticket(client))

