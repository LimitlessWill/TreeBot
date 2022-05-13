from typing import Optional
import discord
from discord import app_commands
from discord.ext import tasks
from os import getenv
import datetime
import extra

# Loading TOKEN from environment variables
TOKEN = getenv('DISCORD_TOKEN')

MY_GUILD = discord.Object(id=970576952257835059)  # replace with your guild id

LOG_CHANNEL = 970576952698220555
APP_ID = 569724616210382875 # from Discord developer portal
CORNJOB_CHANNEL_ID = 971240750731890738



class MyClient(discord.Client):
 def __init__(self, *, intents: discord.Intents, application_id: int):
  super().__init__(intents=intents, application_id=application_id)

 # A CommandTree is a special type that holds all the application command
 # state required to make it work. This is a separate class because it
 # allows all the extra state to be opt-in.
 # Whenever you want to work with application commands, your tree is used
 # to store and work with them.
 # Note: When using commands.Bot instead of discord.Client, the bot will
 # maintain its own tree instead.
  self.tree = app_commands.CommandTree(self)

 # In this basic example, we just synchronize the app commands to one guild.
 # Instead of specifying a guild to every command, we copy over our global commands instead.
 # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
 async def setup_hook(self):
 # This copies the global commands over to your guild.
  self.tree.copy_global_to(guild=MY_GUILD)
  await self.tree.sync(guild=MY_GUILD)


intent = discord.Intents.default()
intent.reactions = True
intent.message_content = True
intent.typing = False
intent.presences = False

# In order to use a basic synchronization of the app commands in the setup_hook,
# you have to replace the 0 with your bot's application_id that you find in the developer portal.
client = MyClient(intents=intent, application_id=APP_ID)

# A cornjob loops every 1 minute (get time send it in a specific channel)
@tasks.loop(minutes=1)
async def test():
 channel = client.get_channel(CORNJOB_CHANNEL_ID)
 cur = datetime.datetime.utcnow().strftime("\t\t\t\t\t    %Y/%B/%d\n\n\t\t\t\t\t\💚  %I:%M  %p  \💚")
 await channel.send(f"\t\t\t\t\t**{cur}**",delete_after=59)


@client.event
async def on_ready():
 print(f"{client.user} has connected to Discord!\nHello World")
 test.start()
 print('------')
 print("test function has started")


@client.tree.command()
async def hello(interaction: discord.Interaction):
 """Says hi!"""
 await interaction.response.send_message(f'Hi, {interaction.user.mention}')


@client.tree.command()
@app_commands.describe(
 first_value='The first value you want to add something to',
 second_value='The value you want to add to the first value')

async def multi(interaction: discord.Interaction, first_value: int, second_value: int):
 """Multiplying two numbers together."""
 await interaction.response.send_message(f'{first_value} * {second_value} = {first_value * second_value}')


# The rename decorator allows us to change the display of the parameter on Discord.
# In this example, even though we use `text_to_send` in the code, the client will use `text` instead.
# Note that other decorators will still refer to it as `text_to_send` in the code.
@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send in the current channel')
async def send(interaction: discord.Interaction, text_to_send: str):
 """Sends the text into the current channel."""
 await interaction.response.send_message(text_to_send)


# To make an argument optional, you can either give it a supported default argument
# or you can mark it as Optional from the typing standard library. This example does both.
@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
 """Says when a member joined."""
 # If no member is explicitly provided then we use the command user here
 member = member or interaction.user

 # The format_dt function formats the date time into a human readable representation in the official client
 await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


@client.event
async def on_message(message):
 await extra.on_message(message)



client.run(TOKEN)
