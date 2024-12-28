import os
from discord.ui import Select
from dotenv import load_dotenv
import model as RAG
import discord
import discord_emoji as emj
from discord import app_commands, SelectOption, Emoji
from math import ceil
import time

load_dotenv()

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
async def split_send(rag_content, message):
    for i in range(ceil(len(rag_content) / 2000)):
        part = (rag_content[(2000 * i): (2000 * (i + 1))])
        await message.channel.send(part)


# init discord client
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

last_prompt_time = time.time() - 5


# class for maps dropdown menu
# super() ensures that parent class init is defaulted
class MapDropdown(discord.ui.Select):
    def __init__(self, author_id):
        self.author_id = author_id
        super().__init__(
            placeholder="Choose a map...",  # Text shown when no option is selected
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=label, value=label, emoji=emoji) for label, emoji in
                     MAPS_EMOJIS.items()],
        )

    async def callback(self, interaction: discord.Interaction):
        # check for valid user
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
        else:
            selected_option = self.values[0]
            await interaction.response.send_message(f"You selected: {selected_option}")


class DropdownView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__()
        self.add_item(MapDropdown(author_id))


# log in message
@client.event
async def on_ready():
    print(f"Bot logged as {client.user}")


# response to messages
@client.event
async def on_message(message):
    global last_prompt_time
    if message.author == client.user:
        return

    # !help message
    if message.content.startswith("!help") and (time.time() - last_prompt_time) >= 5:
        last_prompt_time = time.time()
        print("!help called")
        multiline = ("### :triangular_flag_on_post: **HELP**\n" +
                     "Hello I am AI powered bot who will help you with everything about World of Tanks game and universe :smiley:\n" +
                     "These are my functionalities:\n"
                     "- !wot (message) :arrow_right: for general talk (tanks, equipment, tactics...)\n"
                     "- !map :arrow_right: for map guides")

        await message.channel.send(multiline)

    # !wot chatbot
    if message.content.startswith("!wot ") and (time.time() - last_prompt_time) >= 5:
        last_prompt_time = time.time()
        print("!wot called")
        message_content = message.content[5:]
        rag_response = model.query(message_content, message.author.id)
        print(len(rag_response))
        await  split_send(f"{message.author.mention} " + rag_response, message)

    # !map guides
    if message.content.startswith("!map") and (time.time() - last_prompt_time) >= 5:
        last_prompt_time = time.time()
        print("!map called")
        if message.content != "!map":
            multiline = ("### :exclamation: **Can't help you with that**\n" +
                         "If you wish to get info about specific map use just '!map' and then you will be able to choose one from list\n" +
                         "For further information use !help command\n")
            await  message.channel.send(multiline)
        else:
            view = DropdownView(author_id=message.author.id)
            await message.author.response(content=f"{message.author.mention} Select a map guide:", view=view)


client.run(os.environ.get("DISCORD_API_KEY"))
