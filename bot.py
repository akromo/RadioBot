from discord.ext.commands import Bot
import discord
import config
from youtube_dl import YoutubeDL
import os
import requests
import _thread


#discord.opus.load_opus()
msList = []
names = []

#serverPlayList = {server:[list of sourveses, list of names, current Name]}
serverPlayList = {}



for i in msList:
    if i[-4:] != '.mp3':
        msList.remove(i)

def reloadMusicList(ctx):
    msList = os.listdir(config.MUSPATH)
    sourcesList = [[], msList, 'None']
    for i in msList:
        if i[-4:] != '.mp3':
            msList.remove(i)
    for j in msList:
        sourcesList[0].append(discord.FFmpegPCMAudio(config.MUSPATH + j))
        if len(sourcesList[0]) >= 9:
            break
    serverPlayList[ctx.guild.id] = sourcesList



bot = Bot(command_prefix='!')


def addNewTrack(ctx):
    for i in serverPlayList[ctx.guild.id][1]:
        serverPlayList[ctx.guild.id][0].append(discord.FFmpegPCMAudio(config.MUSPATH + i))
        if len(serverPlayList[ctx.guild.id][0]) >= 9:
            break


def nextSound(ctx):
    vc = ctx.message.guild.voice_client
    #vc.play(serverPlayList[ctx.guild.id][0]), after=lambda e: nextSound(ctx)
    vc.play(serverPlayList[ctx.guild.id][0][0], after=lambda e: nextSound(ctx))
    serverPlayList[ctx.guild.id][0].pop(0)
    serverPlayList[ctx.guild.id][2] = serverPlayList[ctx.guild.id][1].pop(0)
    if len(serverPlayList[ctx.guild.id][0]) <= 3:
        addNewTrack(ctx)


async def on_ready():
    print("Ready")


@bot.command(pass_context=True)
async def join(ctx):
    guild = ctx.message.guild
    if guild.get_role(config.TESTROLE) in ctx.message.author.roles:
        channel = bot.get_channel(config.TESTSERVERVOICE)
        await discord.VoiceChannel.connect(channel)


@bot.command(pass_context=True)
async def leave(ctx):
    guild = ctx.message.guild
    if guild.get_role(config.TESTROLE) in ctx.message.author.roles:
        await guild.voice_client.disconnect()


@bot.command(pass_context=True)
async def play(ctx):
    if len(serverPlayList.keys()) == 0:
        reloadMusicList(ctx)
    guild = ctx.message.guild
    if guild.get_role(config.TESTROLE) in ctx.message.author.roles:
        nextSound(ctx)


@bot.command(pass_context=True)
async def next(ctx):
    guild = ctx.message.guild
    if guild.get_role(config.TESTROLE) in ctx.message.author.roles:
        vc = guild.voice_client
        vc.stop()


@bot.command(pass_context=True)
async def pause(ctx):
    guild = ctx.message.guild
    if guild.get_role(config.TESTROLE) in ctx.message.author.roles:
        vc = guild.voice_client
        vc.pause()


@bot.command(pass_context=True)
async def resume(ctx):
    guild = ctx.message.guild
    if guild.get_role(config.TESTROLE) in ctx.message.author.roles:
        vc = guild.voice_client
        vc.resume()


@bot.command(pass_context=True)
async def name(ctx):
    await ctx.message.channel.send(serverPlayList[ctx.guild.id][2][:-4])


@bot.command(pass_context=True)
async def reset(ctx):
    guild = ctx.message.guild
    if guild.get_role(config.TESTROLE) in ctx.message.author.roles:
        await guild.voice_client.disconnect()
        reloadMusicList(ctx)
        channel = bot.get_channel(config.TESTSERVERVOICE)
        await discord.VoiceChannel.connect(channel)
        nextSound(ctx)


def downloadY(ctx, url):
    info = ydl.extract_info(url, download=False)
    serverPlayList[ctx.guild.id][0].insert(0, discord.FFmpegPCMAudio(info['formats'][1]['url']))  # req.content))
    print('Source %s added in playlist' % ctx.message.content)



@bot.command(pass_context=True)
async def yt(ctx, url):
    _thread.start_new_thread(downloadY, (ctx, url,))


if __name__ == '__main__':
    ydl = YoutubeDL()
    ydl.add_default_info_extractors()
    print('Стартуем')
    bot.run(config.TOKEN)
