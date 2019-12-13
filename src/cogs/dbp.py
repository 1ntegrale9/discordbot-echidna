import discord
from discord.ext import commands
from dispander import compose_embed
from .daug import get_default_embed
from echidna import base36


class DiscordBotPortalJP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.id = 494911447420108820
        self.role_member_id = 579591779364372511
        self.category_issues_id = 601219955035209729
        self.category_open_id = 575935336765456394
        self.category_closed_id = 640090897417240576
        self.close_keywords = [
            'close', 'closes', 'closed',
            'fix', 'fixes', 'fixed',
            'resolve', 'resolves', 'resolved',
        ]

    async def dispatch_thread(self, message):
        channel_issue = await message.guild.create_text_channel(
            name=f'{base36(len(message.guild.text_channels))}-{message.channel.name}',
            category=message.guild.get_channel(self.category_open_id),
        )
        await channel_issue.edit(position=0)
        await channel_issue.send(embed=compose_embed(message))
        await message.channel.send(
            embed=get_default_embed(f'スレッド {channel_issue.mention} を作成しました {message.author.mention}')
        )

    async def dispatch_close(self, channel):
        await channel.edit(
            category=channel.guild.get_channel(self.category_closed_id)
        )

    async def is_category_open(self, message):
        return message.channel.category_id == self.category_open_id

    async def if_category_open(self, message):
        if message.content in self.close_keywords:
            await self.dispatch_close(message.channel)
            return
        await dispatch_age(message)

    def can_rename(self, message):
        if '✅' in message.channel.category.name:
            return True
        if message.channel.category_id == self.category_open_id:
            return True
        return False

    async def dispatch_rename(self, message, name=None, topic=None):
        if name is not None:
            await message.channel.edit(name=name)
        if topic is not None:
            await message.channel.edit(topic=topic)
        await message.delete()

    async def dispatch_age(self, message):
        await message.channel.edit(
            category=category,
            position=0
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id != self.id:
            return
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.channel.TextChannel):
            return
        if self.is_category_open(message):
            await self.if_category_open(message)
        if message.channel.category_id == self.category_issues_id:
            await self.dispatch_thread(message)
        if message.content.startswith('name:') and self.can_rename(message):
            n = len('name:')
            await self.dispatch_rename(message, name=message.content[n:])
        if message.content.startswith('topic:') and self.can_rename(message):
            n = len('topic:')
            await self.dispatch_rename(message, topic=message.content[n:])

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != self.id:
            return
        if member.bot:
            return
        role_member = member.guild.get_role(self.role_member_id)
        await member.add_roles(role_member)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id != self.id:
            return
        if payload.emoji.name != '✅':
            return
        if self.bot.get_user(payload.user_id).bot:
            return
        channel = self.bot.get_channel(payload.channel_id)
        if channel.category_id != self.category_open_id:
            return
        await self.dispatch_close(channel)


def setup(bot):
    bot.add_cog(DiscordBotPortalJP(bot))
