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

    async def dispatch_reopen(self, channel):
        await channel.edit(
            category=channel.guild.get_channel(self.category_open_id)
        )

    async def dispatch_close(self, channel):
        await channel.edit(
            category=channel.guild.get_channel(self.category_closed_id)
        )

    def is_category_open(self, message):
        return message.channel.category_id == self.category_open_id

    async def if_category_open(self, message):
        if message.content in self.close_keywords:
            await self.dispatch_close(message.channel)
            return
        await self.dispatch_age(message)

    def is_category_closed(self, message):
        if '✅' in message.channel.category.name:
            return True
        if '⛔' in message.channel.category.name:
            return True
        return False

    async def dispatch_age(self, message):
        await message.channel.edit(
            position=0
        )

    @commands.command()
    async def name(ctx, *, name):
        conditions = (
            self.is_category_open(ctx.message),
            self.is_category_closed(ctx.message),
        )
        if not any conditions:
            return
        await ctx.channel.edit(name=name)
        await ctx.message.delete()
        await ctx.send(
            embed=get_default_embed(f'チャンネル名を {neme} に変更しました')
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
            return
        if message.channel.category_id == self.category_issues_id:
            await self.dispatch_thread(message)
            return
        if self.is_category_closed(message):
            await self.dispatch_reopen(message.channel)
            return

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
