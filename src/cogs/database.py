import os
import typing
import redis
from discord.ext import commands


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = redis.from_url(
            os.environ['REDIS_URL'],
            decode_responses=True,
        )

    @commands.group()
    async def db(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('オプションを指定してください。')

    @db.command()
    @commands.guild_only()
    async def get(self, ctx, keyword: str):
        key = f'{ctx.guild.id}:{keyword}'
        if not self.redis.exists(key):
            return await ctx.send(f'key:{keyword} は存在しません。')
        await ctx.send(normalize(self.redis.smembers(key)))

    @db.command(aliases=['set'])
    @commands.guild_only()
    async def _set(self, ctx, keyword: str, related: str):
        key = f'{ctx.guild.id}:{keyword}'
        self.redis.sadd(key, related)
        self.redis.sadd(ctx.guild.id, keyword)
        await ctx.send(f'{keyword} に {related} を追加しました。')

    @db.command()
    @commands.guild_only()
    async def delete(self, ctx, keyword: str, related: typing.Optional[str]):
        key = f'{ctx.guild.id}:{keyword}'
        if not self.redis.exists(key):
            return await ctx.send(f'key:{keyword} は存在しません。')
        if related:
            self.redis.srem(key, related)
            await ctx.send(f'key:{keyword} から {related} を削除しました。')
        else:
            self.redis.delete(key)
            self.redis.srem(ctx.guild.id, key)
            await ctx.send(f'key:{keyword} を削除しました。')

    @db.command(aliases=['list'])
    @commands.guild_only()
    async def _list(self, ctx):
        if not self.redis.exists(ctx.guild.id):
            return await ctx.send('データが存在しません。')
        await ctx.send(normalize(self.redis.smembers(ctx.guild.id)))

    @db.command()
    @commands.is_owner()
    async def keys(self, ctx):
        await ctx.send(' '.join(sorted(self.redis.keys())))

    @db.command()
    @commands.is_owner()
    async def flushdb(self, ctx):
        self.redis.flushdb()
        await ctx.send('Deleted all keys in the current database.')

    @commands.command(aliases=['教えて'])
    @commands.guild_only()
    async def oshiete(self, ctx, keyword: str):
        key = f'{ctx.guild.id}:{keyword}'
        if not self.redis.exists(key):
            await ctx.send('？')
        await ctx.send(f'{keyword} は {self.redis.get(key)}')

    @commands.command(aliases=['覚えて'])
    @commands.guild_only()
    async def oboete(self, ctx, keyword: str, related: str):
        _id = ctx.guild.id
        key = f'{_id}:{keyword}'
        self.redis.set(key, related)
        self.redis.sadd(_id, keyword)
        await ctx.send(f'{keyword} は {related}、覚えました！')


def normalize(data):
    return '\n'.join(sorted(data))


def setup(bot):
    bot.add_cog(Database(bot))
