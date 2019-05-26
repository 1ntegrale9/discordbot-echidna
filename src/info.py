from discord import Embed

helps = {
    '/randid':
        'DiscordのIDのダミーを生成します',
    '/randtoken':
        'Discordのアクセストークンをのダミーを生成します',
    '/randcolor':
        'カラーコードを10進数でランダム生成します',
    '/role':
        'サーバーの役職一覧を教えます',
    '/member':
        'サーバーのメンバー人数を教えます',
    '/help':
        'コマンドの一覧と詳細を表示します',
}


async def get_help(client):
    embed = Embed(
        title=client.user.name,
        url='https://github.com/1ntegrale9/discordbot',
        description='powered by discord.py',
        color=0x3a719f)
    embed.set_thumbnail(
        url=client.user.avatar_url)
    for k, v in helps.items():
        embed.add_field(name=k, value=v, inline=False)
    return embed
