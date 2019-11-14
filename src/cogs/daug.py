import discord
from discord import Embed


def get_default_embed(description):
    return Embed.from_dict({
        'description': description,
        'color': discord.Colour.blue().value,
    })
