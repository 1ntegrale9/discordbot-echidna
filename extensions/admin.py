from discord.ext import commands
from Daug.functions.embeds import compose_embed_from_description


class AdministratorFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def create_role(self, ctx, name: str):
        if name.lower() in [role.name.lower() for role in ctx.guild.roles]:
            return await ctx.send('その役職は既に存在します')
        await ctx.guild.create_role(name=name)
        await ctx.send(f'役職 {name} を作成しました')

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def delete_role(self, ctx, name: str):
        for role in ctx.guild.roles:
            if name.lower() == role.name.lower():
                await role.delete()
                return await ctx.send(f'役職 {role.name} を削除しました')
        await ctx.send(f'役職 {name} は存在しません')

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def topic(self, ctx, topic: str):
        await ctx.channel.edit(topic=topic)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx):
        while (await ctx.message.channel.purge()):
            pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def echo(self, ctx, *, text: str):
        await ctx.send(text)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def embed(self, ctx, *, text: str):
        await ctx.send(embed=compose_embed_from_description(text))


def setup(bot):
    bot.add_cog(AdministratorFeatures(bot))
