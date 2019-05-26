from discord import Embed

helps = {
    'role':
        'サーバーの役職一覧を教えます',
    'role ROLENAME(s)':
        '指定した(空白区切り複数の)役職を付与/解除します',
    'create_role ROLENAME':
        '指定した役職を作成します(管理者のみ)',
    'delete_role ROLENAME':
        '指定した役職を削除します(管理者のみ)',
    'member':
        'サーバーのメンバー人数を教えます',
    'help':
        'コマンドの一覧と詳細を表示します',
}


async def get_help(client):
    embed = Embed(
        title=client.user.name,
        url='https://github.com/1ntegrale9/discordbot',
        description='Discord Bot w/ discord.py',
        color=0x3a719f)
    embed.set_thumbnail(
        url=client.user.avatar_url)
    for k, v in helps.items():
        embed.add_field(name=k, value=v, inline=False)
    return embed
