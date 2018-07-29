from functions import run_command
from discord.message import Message
from discord.user import User
from discord.reaction import Reaction
from discord.embeds import Embed
from discord.server import Server
from discord.channel import Channel
from discord import Client
from typing import List
import os
import re
import traceback
import discord
import requests

client = Client()
DEVELOPER = discord.User(id='314387921757143040')
QUOTE_URL_BASE = 'https://discordapp.com/channels/'
scrapbox_api_url = 'https://scrapbox.io/api/pages/'
debug_mode = False


def getDescriptions(projectName, pageTitle):
    url = f'{scrapbox_api_url}/{projectName}/{pageTitle}'
    res = requests.get(url)
    return res.json()['descriptions']


def compose_embed(channel: Channel, message: Message) -> Embed:
    embed = discord.Embed(
        description=message.content,
        timestamp=message.timestamp)
    embed.set_thumbnail(
        url=message.author.avatar_url)
    embed.set_author(
        name=message.author.display_name)
    embed.set_footer(
        text=message.channel.name,
        icon_url=message.server.icon_url)
    return embed


def get_urls(text: str) -> List[str]:
    pattern = QUOTE_URL_BASE + '[0-9]{18}/[0-9]{18}/[0-9]{18}'
    return re.findall(pattern, text)


async def discordurl2embed(client: Client, server: Server, url: str) -> Embed:
    s_id, c_id, m_id = url.split(QUOTE_URL_BASE)[1].split('/')
    if server.id == s_id:
        channel = server.get_channel(c_id)
        message = await client.get_message(channel, m_id)
        return compose_embed(channel, message)
    else:
        return discord.Embed(title='404')


@client.event
async def on_ready() -> None:
    """起動時に実行する"""
    msg = 'ログインしました'
    await client.send_message(DEVELOPER, msg)


@client.event
async def on_message(message: Message) -> None:
    """メッセージ受信時に実行する"""
    try:
        if message.author != client.user:
            await run_command(client, message)
            for url in get_urls(message.content):
                embed = await discordurl2embed(client, message.server, url)
                await client.send_message(message.channel, embed=embed)
    except Exception as e:
        await client.send_message(message.channel, str(e))
        traceback_msg = f'```\n{traceback.format_exc()}\n```'
        await client.send_message(DEVELOPER, traceback_msg)
        if debug_mode:
            await client.send_message(message.channel, traceback_msg)
    else:
        pass
    finally:
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


@client.event
async def on_reaction_add(reaction: Reaction, user: User) -> None:
    """リアクションが付いた時に実行する"""
    if reaction.message.author == DEVELOPER:
        msg = f'{user} が {reaction.message.content} に {reaction.emoji} を付けました'
        await client.send_message(DEVELOPER, msg)


@client.event
async def on_reaction_remove(reaction: Reaction, user: User) -> None:
    """リアクション削除時に実行する"""
    if reaction.message.author == DEVELOPER:
        msg = f'{user} が {reaction.message.content} の {reaction.emoji} を削除しました'
        await client.send_message(DEVELOPER, msg)


def main() -> None:
    client.run(os.environ['DISCORD_BOT_TOKEN'])


if __name__ == '__main__':
    main()
