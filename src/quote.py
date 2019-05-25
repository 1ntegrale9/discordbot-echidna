from discord import Embed
import re


async def expand(message):
    url_discord_message = (
        'https://discordapp.com/channels/'
        r'(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})'
    )
    for ID in re.finditer(url_discord_message, message.content):
        embed = await fetch_embed(ID, message.guild)
        await message.channel.send(embed=embed)


async def fetch_embed(ID, guild):
    if guild.id == ID['guild']:
        channel = guild.get_channel(ID['channel'])
        message = await channel.fetch_message(ID['message'])
        return compose_embed(message)
    else:
        return Embed(title='404')


def compose_embed(message):
    embed = Embed(
        description=message.content,
        timestamp=message.timestamp)
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar_url)
    embed.set_footer(
        text=message.channel.name,
        icon_url=message.guild.icon_url)
    return embed
