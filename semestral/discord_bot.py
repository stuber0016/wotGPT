import os
from discord.ui import Select, View
from discord.ext import commands
from discord import app_commands, Interaction
import discord
from dotenv import load_dotenv
from math import ceil
import time
import discord_emoji as emj

import model as RAG

load_dotenv()

GUILD_ID = discord.Object(id=os.environ.get("GUILD_ID"))

# init RAG model
model = RAG.Model()

MAPS_LABELS = ["Cliff", "El Halluf", "Ensk", "Himmelsdorf", "Karelia", "Mines", "Outpost", "Oyster Bay", "Prokhorovka",
               "Redshire"]
MAPS_EMOJIS = {"Cliff": emj.to_unicode(":rock:"), "El Halluf": emj.to_unicode(":desert:"),
               "Ensk": emj.to_unicode(":house_with_garden:"),
               "Himmelsdorf": emj.to_unicode(":cityscape:"),
               "Karelia": emj.to_unicode(":park:"), "Mines": emj.to_unicode(":pick:"),
               "Outpost": emj.to_unicode(":european_castle:"),
               "Oyster Bay": "<:rice_hat_cat:1322589644956635187>",
               "Prokhorovka": emj.to_unicode(":skull_crossbones:"),
               "Redshire": emj.to_unicode(":sunrise_over_mountains:")}


# splits long messages to parts and sends them one by one
async def split_send(rag_content, interaction):
    for i in range(ceil(len(rag_content) / 2000)):
        part = (rag_content[(2000 * i): (2000 * (i + 1))])
        await interaction.response.send_message(part, ephemeral=True)


# bot class
class Bot(commands.Bot):
    # log in message
    async def on_ready(self):
        print(f"Bot logged as {self.user}")

        # force slash commands sync with discord
        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Synced {len(synced)} commands to guild {GUILD_ID}")
        except Exception as e:
            print(f"Failed syncing commands {e}")

    # avoid answering in loop
    async def on_message(self, message):
        if message.author == self.user:
            return


# init intents
intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix="!", intents=intents)

# used for time out between requests
last_prompt_time = time.time() - 5


# class for maps dropdown menu
# super() ensures that parent class properly initialized
class MapDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=label, emoji=emoji)
            for label, emoji in MAPS_EMOJIS.items()
        ]
        super().__init__(placeholder="Choose a map...", options=options)

    async def callback(self, interaction: discord.Interaction):
        map_name = self.values[0]
        map_filename = self.values[0] + ".png"
        file = discord.File(f"img/{map_filename}", filename=map_filename)
        embed = discord.Embed(title=map_name)
        embed.set_image(url=f"attachment://{map_filename}")
        embed.add_field(
            name="Legend",
            value=(
                "<:light:1322710602946449418> **Light**\n"
                "<:medium:1322710661981147239>  **Med.**\n"
                "<:heavy:1322710615214657616> **Heavy**\n"
                "<:TD:1322710591554457712> **TD**\n"
                "<:arty:1322710568553152522> **SPG**"
            ),
            inline=True
        )
        await interaction.response.send_message(file=file, embed=embed)


# View containing the dropdown
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MapDropdown())


# !help message
@bot.remove_command('help')
@bot.tree.command(name="help", description="Get a list of commands and features", guild=GUILD_ID)
async def help_command(interaction: Interaction):
    global last_prompt_time

    if (time.time() - last_prompt_time) >= 5:
        last_prompt_time = time.time()
        print("/help called")
        multiline = ("### :triangular_flag_on_post: **HELP**\n" +
                     "Hello I am AI powered bot who will help you with everything about World of Tanks game and universe :smiley:\n" +
                     "These are my functionalities:\n"
                     "- /wot (message) :arrow_right: for general talk (tanks, equipment, tactics...)\n"
                     "- /map :arrow_right: for map guides"
                     )
        await interaction.response.send_message(multiline, ephemeral=True)


# !wot chatbot
@bot.tree.command(name="wot", description="Chat about World of Tanks", guild=GUILD_ID)
@app_commands.describe(query="Your query related to World of Tanks")
async def wot_command(interaction: Interaction, query: str):
    global last_prompt_time
    if (time.time() - last_prompt_time) >= 5:
        last_prompt_time = time.time()
        print("!wot called")
        rag_response = model.query(query, interaction)
        await  split_send(rag_response, interaction)


# !map guides
@bot.tree.command(name="map", description="Get guides for maps", guild=GUILD_ID)
async def map_command(interaction: Interaction):
    global last_prompt_time
    if (time.time() - last_prompt_time) >= 5:
        last_prompt_time = time.time()
        print("!map called")
        view = DropdownView()
        await interaction.response.send_message(content="Select a map guide:", view=view,
                                                ephemeral=True)


bot.run(os.environ.get("DISCORD_API_KEY"))
