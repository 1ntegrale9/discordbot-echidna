import asyncio
from discord import TextChannel
from discord.ext import commands
from Daug.functions import excepter


class Prototype(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @excepter
    async def swap(self, ctx, a: TextChannel, b: TextChannel):
        a_name, a_topic, a_position = a.name, a.topic, a.position
        b_name, b_topic, b_position = b.name, b.topic, b.position
        await asyncio.gather(
            a.edit(name=b_name, topic=b_topic, position=b_position),
            b.edit(name=a_name, topic=a_topic, position=a_position)
        )

    @commands.command()
    @commands.guild_only()
    @excepter
    async def get_text_channel(self, ctx, text_channel: TextChannel):
        await ctx.send(text_channel.mention)


def setup(bot):
    bot.add_cog(Prototype(bot))
