from discord import Embed, Colour


def get_default_embed(description):
    return Embed.from_dict({
        'description': description,
        'color': Colour.blue().value,
    })
