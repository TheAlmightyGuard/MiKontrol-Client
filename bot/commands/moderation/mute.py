from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands, Member, Embed, Color, Forbidden
from bot.client import MiBotClient

from typing import Optional
from models.internal import CogModel

from utils.time_functions import add_time
from utils.get_fetch import get_role
from services.moderation_services import add_mute, remove_mute
from services.guild_services import grab_preferred_role

import uuid
import inspect

from rich.console import Console

console = Console()

class Mute(commands.Cog):
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
    # +---------------------+
    # |  Mute Command
    # +---------------------+

    @commands.hybrid_command(
        name="mute",
        description="Mute a specified user"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(5, 2, commands.BucketType.user)
    @app_commands.describe(
        user="Specific user to mute",
        reason="Reason for mute",
        duration_or_reason="Enter reason or duration with number and a suffix of [s/m/h/d]"
    )
    async def mute(self, ctx : commands.Context, user : Member, duration_or_reason : Optional[str] = "No reason provided.", *, reason : str = "No reason provided."):
        
        if user.bot:
            await ctx.send("Yeah, im not muting myself. Smh...", ephemeral=True)
            return

        delta = add_time(duration_or_reason, datetime.now())

        roles = user.roles

        listRoles = []
        for role in roles:
            if not role.is_default():
                listRoles.append(role.id)
                await user.remove_roles(role)

        roleId = await grab_preferred_role(ctx.guild.id, 'muted')

        mutedRole = await get_role(ctx.guild, roleId)
        if mutedRole is None:
            await ctx.send("No muted role found / selected. Skipping...", ephemeral=True, delete_after=5)
            return
        else:
            await user.add_roles(mutedRole)

        actionId = str(uuid.uuid7())

        await add_mute(
            actionId=actionId,
            guildId=ctx.guild.id,
            type='T_MUTE' if isinstance(delta, datetime) else 'MUTE',
            targetId=user.id,
            moderatorId=ctx.author.id,
            listRoles=listRoles,
            expiresAt=delta,
            reason=reason if isinstance(delta, datetime) else duration_or_reason
        )

        embed = Embed(
            title="🔇 Moderator Action",
            description=f"{user.mention} has been muted!",
            timestamp=datetime.now(),
            color=Color.orange()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(
            name="Duration:",
            value=f"<t:{round(delta.timestamp())}:R>" if isinstance(delta, datetime) else "Indefinite"
        )
        embed.add_field(
            name="Reason:",
            value=reason if isinstance(delta, datetime) else duration_or_reason
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
    # |  Unmute Command  |
    # +------------------+

    @commands.hybrid_command(
        name="unmute",
        description="Unmute a specified user"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(5, 2, commands.BucketType.user)
    @app_commands.describe(
        user="Specific user to unmute",
        reason="Reason for unmute"
    )
    async def unmute(self, ctx : commands.Context, user : Member, *, reason : str = "No reason provided."):
        
        result = await remove_mute(
            userId=user.id,
            guildId=ctx.guild.id,
            moderatorId=ctx.author.id,
            reason=reason
        )
        
        if result is None:
            await ctx.send("This person is currently not muted.", ephemeral=True, delete_after=5)
            return

        roles = result.listRoles

        for roleId in roles:

            role = await get_role(ctx.guild, roleId)
            if role is None:
                continue
                    
            await user.add_roles(role)

        mutedRole = await get_role(ctx.guild, await grab_preferred_role(ctx.guild.id, 'muted'))
        if mutedRole is None:
            await ctx.send("No muted role found / selected. Skipping...", ephemeral=True, delete_after=5)
            return
        else:
            await user.remove_roles(mutedRole)


        actionId = str(uuid.uuid7())

        embed = Embed(
            title="🔈 Moderator Action",
            description=f"{user.mention} has been unmuted!",
            timestamp=datetime.now(),
            color=Color.orange()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(
            name="Time remaining:",
            value=f"<t:{round(result.expiresAt.timestamp())}:R>" if isinstance(result.expiresAt, datetime) else "Indefinite",
            inline=True
        )
        embed.add_field(
            name="Reason Given:",
            value=result.reason,
            inline=True
        )
        embed.add_field(
            name="Reason for Removal:",
            value=reason,
            inline=False
        )
        embed.add_field(
            name="Actioned by:",
            value=ctx.author.mention
        )
        embed.set_footer(
            text=f"Action ID: {actionId}",
            icon_url=ctx.author.display_avatar.url 
        )

        await ctx.send(embed=embed)


    # +------------------+
    # |  Error Handler
    # +------------------+

    @mute.error
    async def mute_error(self, ctx : commands.Context, error : commands.CommandError):
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
            console.log(f"Unexpected error! Type: {type(error)} \n Error: {error}")



async def setup(client : MiBotClient):
    await client.add_cog(Mute(client))