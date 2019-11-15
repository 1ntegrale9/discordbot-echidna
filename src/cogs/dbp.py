import discord
from discord.ext import commands
from .quote import compose_embed
from .daug import get_default_embed


class DiscordBotPortalJP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.id = 494911447420108820
        self.role_member_id = 579591779364372511
        self.category_issues_id = 575935336765456394
        self.channel_question_id = 575870793888694274
        self.close_keywords = [
            'close', 'closes', 'closed',
            'fix', 'fixes', 'fixed',
            'resolve', 'resolves', 'resolved',
        ]

    async def dispatch_thread(self, message):
        channel_qa = await message.guild.create_text_channel(
            name=message.author.display_name,
            category=message.guild.get_channel(self.category_issues_id),
        )
        await channel_qa.edit(position=0)
        await message.guild.get_channel(self.channel_question_id).edit(position=0)
        await channel_qa.send(embed=compose_embed(message))
        await message.channel.send(
            embed=get_default_embed(f'スレッド {channel_qa.mention} を作成しました {message.author.mention}')
        )

    async def dispatch_close(self, channel):
        category_closed = discord.utils.get(
            channel.guild.categories,
            position=(channel.category.position + 1)
        )
        await channel.edit(category=category_closed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id != self.id:
            return
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.channel.TextChannel):
            return
        if message.channel.category_id == self.category_issues_id:
            if message.content in self.close_keywords:
                await self.dispatch_close(channel)
        if message.channel.id == self.channel_question_id:
            await self.dispatch_thread(message)

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
        if channel.category_id != self.category_issues_id:
            return
        await self.dispatch_close(channel)


def setup(bot):
    bot.add_cog(DiscordBotPortalJP(bot))
