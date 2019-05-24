from functions import run_command
from functions import expand_quote
import os
import traceback
import redis
import discord

client = discord.Client()
r = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)


@client.event
async def on_ready():
    await client.send_message(
        client.get_channel('502837677108887582'),
        'ログインしました'
        )


@client.event
async def on_message(message):
    try:
        if message.author != client.user:
            await run_command(r, client, message)
            await expand_quote(client, message)
    except Exception as e:
        await client.send_message(message.channel, str(e))
        await client.send_message(
            client.get_channel('502901411445735435'),
            f'```\n{traceback.format_exc()}\n```'
            )


if __name__ == '__main__':
    client.run(os.environ['DISCORD_BOT_TOKEN'])
