import os

import discord.errors
from discord.ext import commands
from discord import app_commands, Interaction, Object, Intents, ui, SelectOption, File, Embed
import discord.errors
from dotenv import load_dotenv
from math import ceil
import discord_emoji as emj
import model as RAG

load_dotenv()

# Change this to your server ID (can be removed completely from all commands below but commands then take a long time to load to the server.
GUILD_ID = Object(id=os.environ.get("GUILD_ID"))

# init RAG model
model = RAG.Model()

MAPS_EMOJIS = {"Cliff": emj.to_unicode(":rock:"), "El Halluf": emj.to_unicode(":desert:"),
               "Ensk": emj.to_unicode(":house_with_garden:"),
               "Himmelsdorf": emj.to_unicode(":cityscape:"),
               "Karelia": emj.to_unicode(":park:"), "Mines": emj.to_unicode(":pick:"),
               "Outpost": emj.to_unicode(":european_castle:"),
               "Oyster Bay": "<:rice_hat_cat:1322589644956635187>",
               "Prokhorovka": emj.to_unicode(":skull_crossbones:"),
               "Redshire": emj.to_unicode(":sunrise_over_mountains:")}

# splits long messages to parts and sends them one by one
MAX_MESSAGE_LENGTH = 2000


async def split_send(rag_content, interaction, file=None, embed=None):
    assert ((file is None and embed is None) or (file is not None and embed is not None))
    parts = ceil(len(rag_content) / MAX_MESSAGE_LENGTH)

    if file is not None:
        await interaction.followup.send(file=file, embed=embed, ephemeral=True)

    for i in range(0, parts):
        part = (rag_content[(MAX_MESSAGE_LENGTH * i): (MAX_MESSAGE_LENGTH * (i + 1))])

        await interaction.followup.send(part, ephemeral=True)


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
intents = Intents.default()
intents.message_content = True
bot = Bot(command_prefix="!", intents=intents)


# class for maps dropdown menu
# super() ensures that parent class is properly initialized
class MapDropdown(ui.Select):
    def __init__(self):
        options = [
            SelectOption(label=label, value=label, emoji=emoji)
            for label, emoji in MAPS_EMOJIS.items()
        ]
        super().__init__(placeholder="Choose a map...", options=options)

    async def callback(self, interaction: Interaction):
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)
        except discord.errors.NotFound:
            print("Interaction not found - may be be reinitialized automatically possible discord API issue")

        await interaction.followup.edit_message(interaction.message.id, content="Thinking...", view=None)

        map_name = self.values[0]
        map_filename = self.values[0] + ".png"
        file = File(f"img/{map_filename}", filename=map_filename)
        embed = Embed(title=map_name)
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

        query = f"How should I play the map: {map_name} with each tank class?"
        rag_response = model.query(query, interaction.user.id)
        await split_send(rag_response, interaction, file=file, embed=embed)


# View containing the dropdown
class DropdownView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MapDropdown())


# /help message
@bot.remove_command('help')
@bot.tree.command(name="help", description="Get a list of commands and features", guild=GUILD_ID)
async def help_command(interaction: Interaction):
    print("/help called")
    multiline = ("### :triangular_flag_on_post: **HELP**\n" +
                 "Hello I am AI powered bot who will help you with everything about World of Tanks game and universe :smiley:\n" +
                 "These are my functionalities:\n"
                 "- /wot (message) :arrow_right: for general talk (tanks, equipment, tactics...)\n"
                 "- /map :arrow_right: for map guides"
                 )
    await interaction.response.send_message(multiline, ephemeral=True)


# /wot chatbot
@bot.tree.command(name="wot", description="Chat about World of Tanks", guild=GUILD_ID)
@app_commands.describe(query="Your query related to World of Tanks")
async def wot_command(interaction: Interaction, query: str):
    print("/wot called")
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
    except discord.errors.NotFound:
        print("Interaction not found - may be be reinitialized automatically possible discord API issue")
    rag_response = model.query(query, interaction.user.id)
    await split_send(rag_response, interaction)


# /map guides
@bot.tree.command(name="map", description="Get guides for maps", guild=GUILD_ID)
async def map_command(interaction: Interaction):
    print("/map called")
    view = DropdownView()
    try:
        await interaction.response.send_message(content="Select a map guide:", view=view, ephemeral=True)
    except discord.errors.NotFound:
        print("Interaction not found - may be be reinitialized automatically possible discord API issue")


# /player-stats personal advice
@bot.tree.command(name="player-stats", description="Get personalised advice based on your gameplay", guild=GUILD_ID)
@app_commands.describe(nickname="Your in-game nickname")
async def stats_command(interaction: Interaction, nickname: str):
    print("/player-stats called")
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
    except discord.errors.NotFound:
        print("Interaction not found - may be be reinitialized automatically possible discord API issue")
    rag_response = model.player_query(nickname, interaction.user.id)
    await split_send(rag_response, interaction)


bot.run(os.environ.get("DISCORD_API_KEY"))
