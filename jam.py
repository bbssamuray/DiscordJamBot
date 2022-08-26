# This example requires the 'members' privileged intents

import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


description = '''
Jam bot   
'''

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

"""----------------------------"""

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------------------------------------------')


@bot.command(aliases=['createteam'])
async def createTeam(ctx,*,teamName:str):
    """To create teams."""
    for role in ctx.author.roles:
        if role.name.startswith("⚪"):
            await ctx.send("You are already in a team.\nGet in contact with moderators for team changes.")
            return
        
    if len(teamName) > 30:
        await ctx.send("Team names cannot be longer than 30 characters.")
        return
    
    if "⚪" in teamName:
        await ctx.send("\"⚪\" character cannot be used in team names.")
        return

    teamName = "⚪" + teamName
    
    for role in ctx.guild.roles:
        if role.name.lower() == teamName.lower():
            await ctx.send("There already is a team with this name.")
            return
    
    role = await ctx.guild.create_role(name=teamName)
    await ctx.author.add_roles(role)
    
    await ctx.send("Team created: " + teamName)
    
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        role: discord.PermissionOverwrite(read_messages=True)
    }

    catChannel = await ctx.guild.create_category_channel(role.name + "🔓", overwrites=overwrites)
    
    textChannel = await catChannel.create_text_channel(role.name)#, overwrites=overwrites)
    voiceChannel = await catChannel.create_voice_channel(role.name)#, overwrites=overwrites)
    
    await textChannel.send("Hello " + "<@" + str(ctx.author.id) + ">!\nYou can talk about your project by text here and by voice in the channel below.\nGood luck!")
    await textChannel.send("Your team is open for new members to join at the moment. They can write `` ?joinTeam Team Name `` to join. To change this, you can write ``?lock`` in this channel.")

@createTeam.error
async def createTeam_error(ctx,error):
    
    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("No team name was given.\n`` ?createTeam Team Name ``")
    else:
        errorMessage = "Something went wrong...\nError:" + str(vars(error))
        await ctx.send(errorMessage)


@bot.command()
async def lock(ctx):
    """To disallow for others to join current team."""
    category = ctx.channel.category
    categoryName = category.name
    
    if categoryName.startswith("⚪"):
        if categoryName.endswith("🔓"):
            await category.edit(name=categoryName[:-1] + "🔒")
            await ctx.send("Team locked🔒, New users can't join now. Type ``?unlock`` to change this.")
        elif categoryName.endswith("🔒"):
            await ctx.send("Team is already locked🔒, other users cannot join this team. Type ``?unlock`` to change this.")
        else:
            await ctx.send("Something went wrong...")
            
        await ctx.send("Note: lock and unlock commands can only be used twice every 10 minutes.")
            
    else:
        await ctx.send("This command can only be used in a team channel.")


@bot.command()
async def unlock(ctx):
    """To allow others to join current team."""
    category = ctx.channel.category
    categoryName = category.name
    
    if categoryName.startswith("⚪"):
        if categoryName.endswith("🔒"):
            await category.edit(name=categoryName[:-1] + "🔓")
            await ctx.send("Team unlocked🔓, users can join this team now. Type ``?lock`` to change this.")
        elif categoryName.endswith("🔓"):
            await ctx.send("Team is already unlocked🔓, other users can join this team. Type ``?lock`` to change this.")
        else:
            await ctx.send("Something went wrong...")
            
        await ctx.send("Note: lock and unlock commands can only be used twice every 10 minutes.")
            
    else:
        await ctx.send("This command can only be used in a team channel.")


@bot.command(aliases=['jointeam'])
async def joinTeam(ctx,*,teamName: str):
    """To join a team."""
    
    for role in ctx.author.roles:
        if role.name.startswith("⚪"):
            await ctx.send("You are already in a team.\nGet in contact with moderators for team changes.")
            return
    
    if "⚪" in teamName:
        await ctx.send("\"⚪\" character cannot be used in team names.")
        return
    teamNotFound = True
    allChannels = await ctx.guild.fetch_channels()
    for channel in allChannels:
        if isinstance(channel,discord.channel.CategoryChannel):
            if channel.name.startswith("⚪"):
                if teamName.lower() == channel.name[1:-1].lower():
                    teamNotFound = False
                    
                    if channel.name.endswith("🔓"):
                        allRoles = await ctx.guild.fetch_roles()
                        for role in allRoles:
                            if (role.name.lower()[1:] == teamName.lower()):
                                await channel.text_channels[0].send("Welcome <@" + str(ctx.author.id) + ">!")
                                await ctx.author.add_roles(role)
                                break
                                
                    elif channel.name.endswith("🔒"):
                        await ctx.send( "Team named " + channel.name[1:] + " is currently locked, for you to join someone in the team has to write ``?unlock`` in the team channel.")
                    else:
                        await ctx.send("An error occured while trying to join.")
    if teamNotFound:
        await ctx.send("Team could not be found.")
                        
@joinTeam.error
async def joinTeam_error(ctx,error):
    
    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("No team name was given.\n`` ?joinTeam Team Name ``")
    else:
        errorMessage = "Something went wrong...\nError:" + str(vars(error))
        await ctx.send(errorMessage)
    
"""----------------------------"""


bot.run(TOKEN)
