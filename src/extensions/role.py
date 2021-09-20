import discord
from discord.ext import commands
from Daug.functions import excepter

bot_user_role_id = 858579302311264266
bot_developers_categories = (
    843437704842706974, # Bot開発者情報共有
    708352513564344370, # Bot開発総合
    858603040093372426, # Bot開発者交流
    788756300582223942, # 共同プロジェクト
)


class AutoDeleteRoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @excepter
    async def on_message(self, message):
        if not isinstance(message.channel, discord.channel.TextChannel):
            return
        if message.channel.category_id not in bot_developers_categories:
            return
        for role in message.author.roles:
            if role.id == bot_user_role_id:
                await message.author.remove_roles(role)


def setup(bot):
    bot.add_cog(AutoDeleteRoleCog(bot))
