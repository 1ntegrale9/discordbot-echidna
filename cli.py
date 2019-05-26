from discord.ext import commands
import os

client = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']


@client.command()
async def do(ctx):
    for channel in ctx.guild.channels:
        payload = {
            'slowmode_delay': 5,
        }
        await channel.edit(**payload)


client.run(token)
