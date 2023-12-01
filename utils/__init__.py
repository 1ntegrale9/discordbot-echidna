import re
import discord


def extract_mentions(guild: discord.Guild, text: str) -> list[discord.Member]:
    return [guild.get_member(int(x)) for x in re.findall(r'<@!?([0-9]{15,20})>', text) if guild.get_member(int(x))]


def extract_role_mentions(guild: discord.Guild, text: str) -> list[discord.Role]:
    return [guild.get_role(int(x)) for x in re.findall(r'<@&([0-9]{15,20})>', text) if guild.get_role(int(x))]


def extract_channel_mentions(guild: discord.Guild, text: str) -> list[discord.abc.GuildChannel]:
    return [guild.get_channel(int(x)) for x in re.findall(r'<#([0-9]{15,20})>', text) if guild.get_channel(int(x))]
