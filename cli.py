from discord.ext import commands
import os

client = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']


def is_developer():
    async def predicate(ctx):
        return ctx.author.id == ID.user.developer
    return commands.check(predicate)


@client.command()
@is_developer()
async def do(ctx):
    for channel in ctx.guild.channels:
        payload = {
            'slowmode_delay': 5,
        }
        await channel.edit(**payload)


client.run(token)
