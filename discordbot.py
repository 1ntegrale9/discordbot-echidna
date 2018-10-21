from functions import run_command
from functions import expand_quote
from typing import List
import os
import traceback
import requests
import redis
import discord

client = discord.Client()
r = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
scrapbox_api_url = 'https://scrapbox.io/api/pages/'


def getDescriptions(
        project_name: str,
        page_title: str
        ) -> List[str]:
    url = f'{scrapbox_api_url}/{project_name}/{page_title}'
    res = requests.get(url)
    return res.json()['descriptions']


@client.event
async def on_ready() -> None:
    """起動時に実行する"""
    await client.send_message(
        client.get_channel('502837677108887582'),
        'ログインしました'
        )


@client.event
async def on_message(
        message: discord.message.Message
        ) -> None:
    """メッセージ受信時に実行する"""
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
    else:
        pass
    finally:
        if message.server:
            log = ''.join([
                str(message.timestamp),
                '\n',
                message.server.name,
                ' ',
                message.channel.name,
                ' ',
                message.author.display_name,
                '\n',
                message.content,
                '\n',
                ])
            print(log)


def main() -> None:
    client.run(os.environ['DISCORD_BOT_TOKEN'])


if __name__ == '__main__':
    main()
