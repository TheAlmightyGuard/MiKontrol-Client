from datetime import datetime
from discord.ext import commands
from discord import app_commands, Embed, Color, Forbidden, User
import discord
from bot.client import MiBotClient
from utils.cogs_functions import cogs_status

from services.moderation_services import add_moderation_log

import uuid

class Kick(commands.Cog):
    def __init__(self, client : MiBotClient):
        self.client = client
    
    async def cog_load(self):
        for command in self.get_commands():
            if isinstance(command, commands.HybridCommand):
                cogs_status(command.name.capitalize(), True)


    # +-----------------+
    # |   Ban Command   |
    # +-----------------+

    @commands.hybrid_command(
        name="kick",
        description="Kick a specified user"
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.cooldown(2, 5, commands.BucketType.user)
    @app_commands.describe(
        user="Specific user to kick",
        reason="Reason for kick"
    )
    async def kick(self, ctx : commands.Context, user : User, *, reason : str = "No reason provided."):
        
        if user.bot:
            await ctx.send("Yeah, im not kicking myself. Smh...", ephemeral=True)
            return

        member = ctx.guild.get_member(user.id)

        if member is None:
            try:
                member = await ctx.guild.fetch_member(user.id)
            except discord.NotFound:
                await ctx.send("The specified user is not found in this server.", ephemeral=True)
                return

        
        actionId = str(uuid.uuid7())

        # Kick User first
        try:
            await ctx.guild.kick(
                user=member,
                reason=reason
            )
        except discord.Forbidden:
            await ctx.send("Unable to kick this user due to permission and/or hierarchy.", ephemeral=True)
            return

        await add_moderation_log(
            actionId=actionId,
            guildId=ctx.guild.id,
            targetId=member.id,
            moderatorId=ctx.author.id,
            type="KICK",
            status="ONCE",
            reason=reason,
            expiresAt=None
        )

        # Embed Creation
        embed = Embed(
            title="🔨 Moderator Action",
            description=f"{member.mention} has been kicked!",
            timestamp=datetime.now(),
            color=Color.orange()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="Reason:",
            value=reason
        )
        embed.add_field(
            name="Issued by:",
            value=ctx.author.mention,
            inline=False
        )
        embed.set_footer(
            text=f"Action ID: {actionId}",
            icon_url=ctx.author.display_avatar.url 
        )

        await ctx.send(embed=embed)

    # +------------------+
    # |  Error Handler   |
    # +------------------+

    # Note to self, somehow error handler is not working, to be investigated later.
    
    @kick.error
    async def kick_error(self, ctx : commands.Context, error : commands.CommandError):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Error! Bad Argument, please input proper arguments!", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions, app_commands.MissingPermissions):
            await ctx.send("Error! You lack permission to execute this command!", ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Error! Bot is missing permissions to execute this command!", ephemeral=True)
        elif isinstance(error, discord.NotFound):
            await ctx.send("Error! The specified user was not found!", ephemeral=True)
        elif isinstance(error, discord.Forbidden) or isinstance(error, Forbidden):
            await ctx.send("Error! Bot lacks the necessary permissions to execute this command!", ephemeral=True)




async def setup(client : MiBotClient):
    await client.add_cog(Kick(client))