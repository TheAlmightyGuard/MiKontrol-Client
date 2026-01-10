from discord.ext import commands

class MiReadyEvent(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('MiKontrol Bot Client is ready!')

async def setup(client: commands.Bot):
    await client.add_cog(MiReadyEvent(client))