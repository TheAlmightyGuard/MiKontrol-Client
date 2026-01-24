import asyncio
from typing import Literal, Optional
from discord.ext import commands
from bot.client import MiBotClient

from models.internal import CogModel
import inspect
import discord

import uuid
from datetime import datetime, timedelta

from bot.modals.ticketModal.genericTicket import GeneralModal
from services.ticket_services import ticket_close

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
    async def ticket(self, ctx : commands.Context):

        if ctx.interaction:
            modal = GeneralModal()

            modal.id = str(uuid.uuid7())

            await ctx.interaction.response.send_modal(modal)

            await modal.wait()
        else:
            await ctx.send("This command can only be used via slash commands (/).", ephemeral=True)

    @ticket.command(
        name="close",
        description="Close a ticket"
    )
    async def close_ticket(self, ctx : commands.Context, *, ticket_id : Optional[str] = None):

        if ctx.interaction:

            result = None

            if ticket_id is None:
                result = await ticket_close(ctx.channel.name, ctx.author.id, reason=f"User ({ctx.author.name}) had closed the ticket.")
            else:
                result = await ticket_close(ticket_id, ctx.author.id, reason=f"User ({ctx.author.name}) had closed the ticket.")

            if result:
                embed = discord.Embed(
                    title="Ticketing System",
                    color=discord.Color.from_str("#ff6b00")
                )
                embed.set_footer(
                    text="Powered by MiKontrol"
                )

                embed.add_field(
                    name=f"Ticket {ticket_id} Closed has been closed by",
                    value=ctx.author.mention
                )

                await ctx.send(embed=embed)

                delta = datetime.now() + timedelta(seconds=10)
                delta = round(delta.timestamp())

                await ctx.send(f"Closing channel <t:{delta}:R>")

                await asyncio.sleep(10)

                await ctx.channel.delete(reason=f"Ticket {ticket_id} Closed has been closed by {ctx.author.name}")

            else:
                await ctx.send("No ticket was found")
        else:
            await ctx.send("This command can only be used via slash commands (/).", ephemeral=True)


async def setup(client: MiBotClient):
    await client.add_cog(Ticket(client))

