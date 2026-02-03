from discord.ext import commands
from rich.console import Console
from services.task_services import sync_ticket_channels
console = Console()
class MiReadyEvent(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        console.log('MiKontrol Bot Client is ready!')

        await sync_ticket_channels(self.client)

        console.log("Ticket Channels SYNCED!")

async def setup(client: commands.Bot):
    await client.add_cog(MiReadyEvent(client))