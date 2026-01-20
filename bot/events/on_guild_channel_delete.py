from discord.ext import commands
from services.ticket_services import ticket_close
from rich.console import Console

import discord

console = Console()

class MiChannelDelete(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel : discord.TextChannel):

        async for audit in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
            await ticket_close(
                ticket_id=channel.name,
                interaction_user=audit.user_id,
                reason=f"User ({audit.user.name if audit.user is not None else "Unknown"}) had deleted the channel."
            )
       
async def setup(client: commands.Bot):
    await client.add_cog(MiChannelDelete(client))