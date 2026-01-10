from discord import Embed, Color, Member
from models.moderation import WarningEntry
from datetime import datetime

def create_warning_embed(warnings: list[WarningEntry], currentIndex: int, moderator: Member, target: Member) -> Embed:

    targetWarning = warnings[currentIndex]
    dateIssued = round(targetWarning.createdAt.timestamp())

    embed = Embed(
        title=f'📜 User Warnings [{currentIndex + 1}/{len(warnings)}]',
        description=f'Moderation records for {target.mention}',
        timestamp=datetime.now(),
        color=Color.orange()
    )
    embed.set_author(
        name=f'Requested by: {moderator.name}',
        url=moderator.avatar.url if moderator.avatar else 'https://placehold.co/130'
    )

    embed.set_thumbnail(
        url=target.avatar.url if target.avatar else 'https://placehold.co/130'
    )

    embed.add_field(
        name="Action ID",
        value=targetWarning.actionId,
        inline=True
    )
    embed.add_field(
        name="Guild ID",
        value=targetWarning.guildId,
        inline=True
    )
    embed.add_field(
        name="Date of Issue",
        value=f"<t:{dateIssued}:f>",
        inline=False
    )
    embed.add_field(
        name="Moderator",
        value=moderator.mention,
        inline=True
    )
    embed.add_field(
        name="Moderation Reason",
        value=targetWarning.reason,
        inline=True
    )

    embed.set_footer(
        text=f'Page [{currentIndex + 1}/{len(warnings)}]',
        icon_url=moderator.avatar.url if moderator.avatar else 'https://placehold.co/130'
    )

    return embed


def create_empty_embed(moderator: Member, target: Member) -> Embed:

    embed = Embed(
        title=f'📜 User Warnings [0/0]',
        description=f'Moderation records for {target.mention}',
        timestamp=datetime.now(),
        color=Color.orange()
    )
    embed.set_author(
        name=f'Requested by: {moderator.name}',
        url=moderator.avatar.url if moderator.avatar else 'https://placehold.co/130'
    )

    embed.set_thumbnail(
        url=target.avatar.url if target.avatar else 'https://placehold.co/130'
    )

    embed.add_field(
        name="Result:",
        value="No warnings found.",
        inline=True
    )

    embed.set_footer(
        text=f'Page [0/0]',
        icon_url=moderator.avatar.url if moderator.avatar else 'https://placehold.co/130'
    )

    return embed