from discord.ext import commands
from services.guild_services import guild_join

import discord

class MiGuildJoin(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild : discord.Guild):
        await guild_join(
            serverId=guild.id,
            prefix="!",
            locale=guild.preferred_locale.language_code,
            premiumLevel=guild.premium_tier
        )

        # Below this will initiate the welcome system

async def setup(client: commands.Bot):
    await client.add_cog(MiGuildJoin(client))