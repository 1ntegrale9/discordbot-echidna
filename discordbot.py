from functions import run_command
from discord.message import Message
from discord.user import User
from discord.reaction import Reaction
from discord import Client
import os
import traceback
import discord

client = Client()
DEVELOPER = discord.User(id='314387921757143040')
debug_mode = False


@client.event
async def on_ready() -> None:
    """起動時に実行する"""
    print('Logged in')
    await client.edit_profile(username="Echidna")


@client.event
async def on_message(message: Message) -> None:
    """メッセージ受信時に実行する"""
    try:
        if message.author != client.user:
            await run_command(client, message)
    except Exception as e:
        await client.send_message(message.channel, str(e))
        traceback_msg = f'```\n{traceback.format_exc()}\n```'
        await client.send_message(DEVELOPER, traceback_msg)
        if debug_mode:
            await client.send_message(message.channel, traceback_msg)
    else:
        pass
    finally:
        pass


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
