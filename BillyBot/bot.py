import datetime
import discord
import srcomapi, srcomapi.datatypes as dt
import os
import re
from datetime import timedelta
from discord.ext import commands
from dotenv import load_dotenv

#Load token from environment variable
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = '!')

#Load Speedrun.com API
api = srcomapi.SpeedrunCom()
game = (api.search(dt.Game, {"name": "billy hatcher and the giant egg"}))[0]

#Edit list of help commands here
client.remove_command('help')  #Override default help command
help_string = '''__**Commands:**__
**!docs:** Links to speedrunning documentation.
**!help:** Gives a list of commands.
**!il (level):** Gives the current world record time for a specified level.
**!misc:** Links to leaderboards and submission form for miscellaneous categories.
**!moviegoer/!unmoviegoer:** Gives/Revokes the Moviegoers role.
**!splits:** Links to the download for splits.
**!tech (technique):** Gives information on a certain technique or lists all techniques if no args are provided.
**!wr any%/all/100%:** Gives the current world record time for any%/all levels/100%.
'''

#Edit list of techniques here (This is DISGUSTING, use text files if you dare)
techniques = {
    "bounce":   {"object":      "__**Object Bounce**__" +
                                "\n**Used in:** 2-5, 3-2, 6-2, 7-1, 1-2, 5-2, 6-1, 6-3" +
                                "\n**How to perform:** Bounce on the edge of an object and hold the direction into the object on the joystick. " +
                                "Once flung out, switch to holding towards where you're going. " +
                                "\n**Useful videos:** https://youtu.be/jT233rAoaTk" +
                                "\n**Practice notes:** Go to 3-2, and perform the bounce shown in the video. " +
                                "Try to get it consistent, and go all the way to the green hoop area to the right.",
                 "esb":         "__**ESB (Egg Shoot Bounce)**__" +
                                "\n**Used in:** 3-8, 5-2, 5-3, 6-2" +
                                "\n**How to perform:** Both eggs must be the same size or one must be an elder egg. " +
                                "Place an egg down (preferably in a corner). Shoot another egg out, directly away from the corner. " +
                                "Grab the back egg and bounce, holding the direction of the egg that's returning to you. " +
                                "Once you bounce, release the stick and hold neutral if going straight up, or hold in the direction you want to go." +
                                "\n**Useful videos:** https://youtu.be/bgtM-3Jspac?t=2593 & https://youtu.be/i3XkGqbN4Ak?t=20" +
                                "\n**Practice notes:** I would recommend learning this on 3-8 or 6-2 as shown in the videos. " +
                                "The land can mess with the timing a little bit, but these are the most commonly used and share the same timing " +
                                "(hill in 3-8 and the floor gate in 6-2 delay it about the same)."},
    "ricochet": {"edr":         "__**EDR (Egg Dash Ricochet)**__" +
                                "\n**Used in:** 3-8, 5-1, 5-2, 7-1" +
                                "\n**How to perform:** Place one egg against a wall (works best in a corner). " +
                                "This can be made easier by giving it a tap into place with another egg. Dash directly into the egg and jump when you hit it. " +
                                "If you need some extra height, dash at the corner the egg is placed in rather than perpendicular." +
                                "\n**Useful videos:** https://youtu.be/uN9QEsQxObA & https://youtu.be/whsteOK0Cl0" +
                                "\n**Practice notes:** Go to 5-1 where you hatch the golden egg, and perform the ricochet shown in the first video. " +
                                "Pressing up against the left side wall as you dash tends to make it more consistent. Also, this trick is sort of going out of style, " +
                                "as there are alternatives like ESB which are less dependent on strict corners and egg tilts. " +
                                "Therefore it's only really potentially useful on 5-1 for the most part.",
                 "esedr":       "__**ESEDR (Egg Shoot Egg Dash Ricochet)**__" +
                                "\n**Used in:** 5-1, 5-2" +
                                "\n**How to perform:** This is essentially a combination of an ESB and EDR. Shoot an egg, then as it's returning, perform a EDR off it. " +
                                "The timing is a little earlier than a traditional EDR because the egg is moving towards you. " +
                                "Eggs must be the same size, or one must be the elder egg." +
                                "\n**Useful videos:** https://youtu.be/8vtw49vampw?t=1559 & https://youtu.be/V_O8R7GK7wc?t=37" +
                                "\n**Practice notes:** This is a relatively new movement tech, so it only currently sees use on 5-1 except for Kosmic on 5-2. " +
                                "5-1 w/ the elder egg is a bit of a special case because the difference in egg sizes greatly affects the timing. " +
                                "I would just learn 5-1 for now, but if you're interested, there are other places to implement it (but no videos yet).",
                 "combos":      "__**Combinations**__" +
                                "\n**Used in:** 3-8, 5-2, 6-2, 7-1" +
                                "\n**How to perform:** Ricochets are very powerful when combined with a bounce off an object, " +
                                "because you maintain your speed and are able to change direction. " +
                                "This is a bounce, but with an object in the path of your bounce to ricochet off." +
                                "\n**Useful videos:** https://youtu.be/8vtw49vampw?t=3026 & https://youtu.be/8vtw49vampw?t=3705" +
                                "\n**Practice notes:** I would learn the object bounce->egg ricochet in 3-8 and 7-1. Both of these are the expectation currently. " +
                                "7-1 may be a bit easier and also saves more time, so start with that."},
    "boost":    {"object":      "__**Object Boost**__" +
                                "\n**Used in:** 3-8, 5-1, 6-2" +
                                "\n**How to perform:** Perform a driver attack on top of an object (bounce + hold A). " +
                                "This will send you upwards and hopefully onto a platform. This technique is not used often because " +
                                "it usually removes the player's ability to air roll and does not yield much height. Mostly useful as a backup in 3-8." +
                                "\n**Useful videos:** https://youtu.be/gcP5hnzaXm8?t=25" +
                                "\n**Practice notes:** I would learn the boost in 3-8.",
                 "emb":         "__**EMB (Egg Multi Boost)**__" +
                                "\n**Used in:** 3-8, 5-2, 6-2, 6-3" +
                                "\n**How to perform:** Place an egg in a corner. Grab another egg and bounce on top of the other one. " +
                                "Hold into the corner as you descend, and when Billy starts moving upwards off the other egg, go neutral on the controller." +
                                "\n**Useful videos:** https://youtu.be/n5rt95_d50k & https://youtu.be/19CafxE3-xw" +
                                "\n**Practice notes:** I would learn both the 6-3 and 5-2 boosts." +
                                "They are both very easy to pick up and lose minimal time (see comparison video). This is a new strat, so the name is WIP. " +
                                "I feel like these are more similar to ricochets then boosts, but our community hasn't agreed on all the naming conventions yet."},
    "clip":     {"enemy kbc":   "__**Enemy KBC (Knockback Clip)**__" +
                                "\n**Used in:** 1-6, 4-2, 6-2, 7-1" +
                                "\n**How to perform:** Grab an egg from the side facing a wall. Hop backwards while baiting an enemy near the wall. " +
                                "Land on top of their hitbox while perpendicular to the wall and you will clip through. " +
                                "Make sure not to get too close to the wall while \"back hopping\" because it will offset your angle to the side. " +
                                "If need be, you can stall your spot in the air a bit with a driver attack (jump or bounce + hold A). " +
                                "This is useful for cats and bees." +
                                "\n**Useful videos:** https://youtu.be/J73D8l5cyUs & https://youtu.be/8vtw49vampw?t=1357" +
                                "\n**Practice notes:** I would learn the clip in 4-2 (second video), and the bee clip in 1-6. " +
                                "Fami skip in 6-2 is also an example of this type of KBC but is very advanced.",
                 "egg kbc":     "__**Egg KBC (Knockback Clip)**__" +
                                "\n**Used in:** 1-1, 1-3" +
                                "\n**How to perform:** Position two eggs, one a little away from the wall, and one further away just in front of it. " +
                                "The further egg must be larger than the egg you're going to clip with. " +
                                "Shoot the larger egg, run around to the back of the smaller one, and jump. " +
                                "Then, after jumping, hold the direction towards the wall and you should clip."
                                "\n**Useful videos:** https://youtu.be/H6Ii_l08Y5U?t=60" +
                                "Practice notes: I would learn the clip in 1-1. Egg KBCs are, in most people's opinion, easier than normal KBCs. " +
                                "Because it requires two eggs, one of which is larger, it's usually used as more of a backup strat (especially in all levels). " +
                                "1-1 is the real mainstream egg KBC, and 1-3 also has one that some people do in runs.",
                 "billy":       "__**Billy Clip**__" +
                                "\n**Used in:** 6-3" +
                                "\n**How to perform:** Press Billy up against the wall to the right of the door and center your camera (L bumper). " +
                                "Release joystick and then hold up + left."
                                "\n**Useful videos:** https://youtu.be/Hi2EA7LnJ14?t=75" +
                                "\n**Practice notes:** This is super easy. Essentially mandatory for everyone to know this skip. " +
                                "There is a different type of clip called an \"egg-shoot clip\" which only is useful in 1-1, " +
                                "but it's essentially TAS only so don't worry about it for now."},
    "misc":                     "__**Miscellaneous**__" +
                                "\nWhen out of bounds, you can hit an object hitbox and warp upwards quite a ways. " +
                                "This is fun but only proved to be useful in 4-2 during a tas."  +
                                "\nYou can build up infinite speed on slopes and such (https://youtu.be/bn1ePPWyXis?t=117). " +
                                "Not useful because it takes too long to build up the speed." +
                                "\nYou can instantly get into hoops by rolling into them. This is used in the 5-5 il speedrun, " +
                                "and it a small thing that can save a bit over the course of the run." +
                                "\nBilly does a recovery or \"get up\" animation when you press A after rolling. " +
                                "You can skip this if you press A on a frame where billy and the egg intersect two planes ground. " +
                                "This happens often on the edges of slopes like 2-1. " +
                                "This also happens if after a fall you land with billy on the side of the egg where he would be after recovering. " +
                                "This video doesn't do it: https://youtu.be/KJtf9JSvcd4?t=50 , this one does: https://youtu.be/b0WIJKwvrj0?t=41"
}

#Returns string with run info
def get_time_string(ctx, category):
    time_string = ""
    run_time = datetime.datetime.strptime(str(datetime.timedelta(seconds=category.records[0].runs[0]["run"].times["primary_t"])), '%H:%M:%S')
    run_time_string = run_time.strftime('%H:%M:%S')
    player = str(category.records[0].runs[0]["run"].players[0]).split()[1][1:-2]
    time_string = "The current record for **{}** is **{}** by **{}**.".format(str(category).split(maxsplit=1)[1][1:-2], run_time_string, player)
    time_string += "\nLink: {}".format(category.records[0].runs[0]["run"].weblink)
    return time_string

#"Overload" of previous method for IL times
def get_time_string_il(ctx, il, level):
    time_string = ""
    run_time = datetime.datetime.strptime(str(datetime.timedelta(seconds=il.runs[0]["run"].times["primary_t"])), '%H:%M:%S.%f')
    run_time_string = run_time.strftime('%M:%S.%f')[:-3]
    player = str(il.runs[0]["run"].players[0]).split()[1][1:-2]
    time_string = "The current record for **{}** is **{}** by **{}**.".format(level.name, run_time_string, player)
    time_string += "\nLink: {}".format(il.runs[0]["run"].weblink)
    return time_string

#Bot startup
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('!help'))
    print("Good morning!")

#Gives command list
@client.command()
async def help(ctx):
    await ctx.send(help_string)

#Gives world record time for any%/all levels/100%
@client.command()
async def wr(ctx, *args):
    if len(args) == 0:
        await ctx.send("Plase specify any%, all levels, or 100%.")
    else:
        arg = ' '.join(args)
        if arg == 'any' or arg == 'any%':
            category = game.categories[0]
            await ctx.send(get_time_string(ctx, category))
        elif arg == 'all' or arg == 'all levels':
            category = game.categories[1]
            await ctx.send(get_time_string(ctx, category))
        elif arg == "100" or arg == '100%':
            category = game.categories[2]
            await ctx.send(get_time_string(ctx, category))
        else:
            await ctx.send("Plase specify any%, all levels, or 100%.")
        
#Gives world record time for ILs
@client.command()
async def il(ctx, *args):
    if len(args) == 0:
        await ctx.send("Please specify a valid level.")
    else:
        arg = ' '.join(args)
        category = game.categories[3]
        valid = re.search(r'[1-7]-[1-8]', arg)
        if valid:
            level = game.levels[(int(arg[0])-1)*8 + (int(arg[2])-1)]
            il = dt.Leaderboard(api, data=api.get("leaderboards/{}/level/{}/{}?embed=variables".format(game.id, level.id, category.id)))
            await ctx.send(get_time_string_il(ctx, il, level))
        else:
            await ctx.send("Please specify a valid level.")

#Gives moviegoers role
@client.command()
async def moviegoer(ctx):
    member = ctx.author
    role = discord.utils.get(member.guild.roles, name="Moviegoers")
    await discord.Member.add_roles(member, role)
    await ctx.send("{} has entered the theater.".format(member.mention))

#Removes moviegoers role
@client.command()
async def unmoviegoer(ctx):
    member = ctx.author
    role = discord.utils.get(member.guild.roles, name="Moviegoers")
    await discord.Member.remove_roles(member, role)
    await ctx.send("{} has left the theater.".format(member.mention))

#Links to download for splits
@client.command()
async def splits(ctx):
    await ctx.send("https://drive.google.com/drive/u/2/folders/103lE_I8gwDDrzc3cNxzDi-INk_iIkSw6")

#Links to speedrun docs
@client.command()
async def docs(ctx):
    await ctx.send("https://drive.google.com/drive/u/2/folders/1_aQQbAgWYq4ML5JhYohlzxEOcgzMdf09")

#Links to misc categories & submission form
@client.command()
async def misc(ctx):
    await ctx.send("Misc. Leaderboards: https://docs.google.com/spreadsheets/d/1Q3E5ZcQno8Bt1-q01j06m1td3GfKBYTgvvpT-Kl2gHA/edit#gid=0" +
    "\nMisc. Category Submission Form: https://docs.google.com/forms/d/e/1FAIpQLScOB_6sOhd4OhNfHUxiZMDUPqIxBiobz5r8svasrxIGpAlcFA/viewform")

#Gives info about techniques, this code is supremely lazy
@client.command()
async def tech(ctx, *args):
    tech_string = ""

    #No argument provided
    if len(args) == 0:
        tech_string = "**List of techniques: **"
        for category in techniques:
            tech_string += "{}, ".format(category)
        await ctx.send(tech_string[:-2])
        return
    else:
        arg = ' '.join(args) 

        #General categories
        if arg == "bounce":
            tech_string = "**List of bounces: **"
            for category in techniques["bounce"]:
                tech_string += "{}, ".format(category)
            await ctx.send(tech_string[:-2])
            return
        if arg == "ricochet":
            tech_string = "**List of ricochets: **"
            for category in techniques["ricochet"]:
                tech_string += "{}, ".format(category)
            await ctx.send(tech_string[:-2])
            return
        if arg == "boost":
            tech_string = "**List of boosts: **"
            for category in techniques["boost"]:
                tech_string += "{}, ".format(category)
            await ctx.send(tech_string[:-2])
            return
        if arg == "clip":
            tech_string = "**List of clips: **"
            for category in techniques["clip"]:
                tech_string += "{}, ".format(category)
            await ctx.send(tech_string[:-2])
            return
        if arg == "misc":
            await ctx.send(techniques["misc"])
            return

        #Bounces
        vals = ["object bounce", "objectbounce", "sign", "signbounce", "sign bounce"]  #Object bounce
        if arg in vals:
            await ctx.send(techniques["bounce"]["object"])
            return
        vals = ["esb", "egg shoot bounce", "eggshootbounce"]  #ESB
        if arg in vals:
            await ctx.send(techniques["bounce"]["esb"])
            return

        #Ricochets
        vals = ["edr", "egg dash ricochet"]  #EDR
        if arg in vals:
            await ctx.send(techniques["ricochet"]["edr"])
            return
        vals = ["esedr", "egg shoot egg dash ricochet", "pedr"]  #ESEDR
        if arg in vals:
            await ctx.send(techniques["ricochet"]["esedr"])
            return
        vals = ["combo", "combination", "combos", "combinations"]  #Combinations
        if arg in vals:
            await ctx.send(techniques["ricochet"]["combos"])
            return

        #Boosts
        vals = ["object boost", "objectboost"]  #Object boost
        if arg in vals:
            await ctx.send(techniques["boost"]["object"])
            return
        vals = ["emb", "egg multi boost", "egg multiboost", "egg multi-boost"]  #EMB
        if arg in vals:
            await ctx.send(techniques["boost"]["emb"])
            return

        #Clips
        vals = ["enemy kbc", "enemykbc", "enemy clip", "enemyclip"]  #Enemy KBC
        if arg in vals:
            await ctx.send(techniques["clip"]["enemy kbc"])
            return
        vals = ["egg kbc", "eggkbc", "egg clip", "eggclip"]  #Egg KBC
        if arg in vals:
            await ctx.send(techniques["clip"]["egg kbc"])
            return
        vals = ["billy", "billy clip", "billyclip"]  #Billy clip
        if arg in vals:
            await ctx.send(techniques["clip"]["billy"]) 
            return   

        #Invalid argument
        await ctx.send("Please specify a valid technique.")

#General command parsing
@client.event
async def on_message(msg):
    msg.content = msg.content.lower()
    if msg.author.id == client.user.id:
        return
    if msg.content == "billy":
        await msg.channel.send("billy")
    else:
        await client.process_commands(msg)

#Lazy error handler
@client.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.CommandError):
        await ctx.send("Invalid command. Type !help for help.")

client.run(TOKEN)
