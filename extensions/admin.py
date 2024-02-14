import io
import discord
from time import time
from discord.ext import commands
from daug.utils.dpyexcept import excepter

USER_ADMIN_ID = 314387921757143040
CHANNEL_ON_GUILD_JOIN_ID = 1207463189894397962


def compose_channels_tree(guild):
    tree = []
    for category in guild.by_category():
        if category[0] is None:
            tree.append('C#')
        else:
            tree.append(f'C# {category[0].id} {category[0].name}')
        for channel in category[1]:
            if isinstance(channel, discord.channel.TextChannel):
                tree.append(f'  T# {channel.id} {channel.name}')
            if isinstance(channel, discord.channel.VoiceChannel):
                tree.append(f'  V# {channel.id} {channel.name}')
    return '\n'.join(tree)


def compose_roles_tree(guild):
    return '\n'.join([f'{role.id} {role.name}' for role in guild.roles])


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @excepter
    async def on_ready(self):
        for guild in self.bot.guilds:
            if guild.get_member(USER_ADMIN_ID) is None:
                await guild.leave()

    @commands.Cog.listener()
    @excepter
    async def on_guild_join(self, guild):
        await self.bot.get_channel(CHANNEL_ON_GUILD_JOIN_ID).send(f'{guild.id}:{guild.name}')
        if guild.get_member(USER_ADMIN_ID) is None:
            await guild.leave()

    @commands.command()
    @excepter
    async def get_info(self, ctx):
        if ctx.author.id != USER_ADMIN_ID:
            return
        for guild in self.bot.guilds:
            await ctx.author.send(
                content=guild.name,
                files=(
                    discord.File(
                        io.StringIO(compose_channels_tree(guild)),
                        f'{guild.id}_channels_{int(time())}.txt',
                    ),
                    discord.File(
                        io.StringIO(compose_roles_tree(guild)),
                        f'{guild.id}_roles_{int(time())}.txt',
                    ),
                )
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))
