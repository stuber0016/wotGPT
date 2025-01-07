"""
discord_bot.py - World of Tanks Discord Bot Module

This module implements a Discord bot for World of Tanks players, providing various
functionalities through slash commands and interactive elements.

Key components:
- Bot class: Custom implementation of discord.ext.commands.Bot
- MapDropdown and DropdownView: UI elements for map selection
- Slash commands: /help, /wot, /map, /player-stats

Main features:
- General World of Tanks queries (/wot)
- Map guides with interactive selection (/map)
- Live player statistics and personalized advice (/player-stats)
- Help command for bot usage information (/help)

The bot utilizes a RAG (Retrieval-Augmented Generation) model for answering queries
and providing advice. It also handles message splitting for long responses and
includes error handling for Discord API interactions.

Dependencies:
- discord.py: For Discord bot functionality
- dotenv: For loading environment variables
- model: Custom module for RAG model implementation

Note: Requires DISCORD_API_KEY and GUILD_ID environment variables.
      Some emojis used are custom and must be added to the Discord server.
      You can find them in img/emojis folder.
"""
from math import ceil
import os

from discord.app_commands import CommandSyncFailure
from discord.ext import commands
from discord import app_commands, Interaction, Object, Intents, ui, SelectOption, File, Embed
import discord.errors
from dotenv import load_dotenv
import discord_emoji as emj

import model as rag

# load env variables
load_dotenv()

# Change this to your server ID (can be removed completely from all commands below but commands then take a long time to load to the server).
GUILD_ID = Object(id=os.environ.get("GUILD_ID"))
if GUILD_ID is None:
    raise ValueError("GUILD_ID environment variable is not set")

# init RAG model
try:
    model = rag.Model()
except ValueError as e:
    raise ValueError(e)

# Some emojis are custom THEY MUST BE ADDED TO YOUR SERVER otherwise the bot will crash.
MAPS_EMOJIS = {"Cliff": emj.to_unicode(":rock:"), "El Halluf": emj.to_unicode(":desert:"),
               "Ensk": emj.to_unicode(":house_with_garden:"),
               "Himmelsdorf": emj.to_unicode(":cityscape:"),
               "Karelia": emj.to_unicode(":park:"), "Mines": emj.to_unicode(":pick:"),
               "Outpost": emj.to_unicode(":european_castle:"),
               "Oyster Bay": "<:rice_hat_cat:1322589644956635187>",
               "Prokhorovka": emj.to_unicode(":skull_crossbones:"),
               "Redshire": emj.to_unicode(":sunrise_over_mountains:")}

MAX_MESSAGE_LENGTH = 2000


async def split_send(rag_content, interaction, file=None, embed=None):
    """
    Sends a message, splitting it if too long. Optionally sends a file and embed.

    Args:
        rag_content (str): Message to send.
        interaction: Discord interaction object.
        file (Optional): File to send. Requires embed.
        embed (Optional): Embed to send. Requires file.

    Raises:
        AssertionError: If only file or only embed is provided.
    """
    assert ((file is None and embed is None) or (file is not None and embed is not None))
    parts = ceil(len(rag_content) / MAX_MESSAGE_LENGTH)

    if file is not None:
        await interaction.followup.send(file=file, embed=embed, ephemeral=True)

    for i in range(0, parts):
        part = (rag_content[(MAX_MESSAGE_LENGTH * i): (MAX_MESSAGE_LENGTH * (i + 1))])

        await interaction.followup.send(part, ephemeral=True)


class Bot(commands.Bot):
    """
    Custom Discord bot class extending commands.Bot.
    """

    async def on_ready(self):
        """
        Coroutine called when the bot is ready.
        Logs the bot's user and syncs slash commands with Discord.
        """
        print(f"Bot logged as {self.user}")

        # force slash commands sync with discord
        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Synced {len(synced)} commands to guild {GUILD_ID}")
        except CommandSyncFailure as e:
            print(f"Failed syncing commands {e}")

    async def on_message(self, message, /):
        """
        Coroutine called when a message is received.
        Prevents the bot from responding to its own messages.

        Args:
            message: The received message object.
        """
        if message.author == self.user:
            return


# Initialize Discord bot with custom intents
# This setup allows the bot to access message content and respond to commands

# Create default intents for the bot
intents = Intents.default()

# Enable the message content intent
# This allows the bot to read the content of messages, which is necessary for many functionalities
intents.message_content = True

# Initialize the bot with a command prefix and the configured intents
# The '!' prefix means the bot will respond to commands starting with '!' -> BUT currently using only slash commands
bot = Bot(command_prefix="!", intents=intents)


class MapDropdown(ui.Select):
    """
       A dropdown menu for selecting maps.

       Attributes:
           options (list): List of SelectOption objects for each map.

       Methods:
           callback(interaction): Handles the selection of a map.
       """

    def __init__(self):
        """Initialize the dropdown with map options."""
        options = [
            SelectOption(label=label, value=label, emoji=emoji)
            for label, emoji in MAPS_EMOJIS.items()
        ]
        super().__init__(placeholder="Choose a map...", options=options)

    async def callback(self, interaction: Interaction):
        """
            Handle map selection.

            Args:
                interaction (Interaction): The interaction that triggered the callback.

            This method:
            1. Defers the interaction response.
            2. Updates the message to show "Thinking...".
            3. Prepares and sends an embed with the selected map image and legend.
            4. Queries a model for map strategy and sends the response.
            """
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)
        except discord.errors.NotFound:
            print("Interaction not found - may be be reinitialized automatically possible discord API issue")

        await interaction.followup.edit_message(interaction.message.id, content="Thinking...", view=None)

        map_name = self.values[0]
        map_filename = self.values[0] + ".png"
        file = File(f"img/maps/{map_filename}", filename=map_filename)
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

        query = f"How should I play on the map: {map_name}?"
        rag_response = model.query(query, interaction.user.id)
        await split_send(rag_response, interaction, file=file, embed=embed)


class DropdownView(ui.View):
    """
        A view containing the MapDropdown.

        This class creates a UI view with the map selection dropdown.
        """

    def __init__(self):
        """Initialize the view and add the MapDropdown."""
        super().__init__()
        self.add_item(MapDropdown())


# All methods below are slash commands which respond to the user via Discord Interactions that are visible only to the
# user who invoked them. This is done by setting the ephemeral flag to True.


@bot.remove_command('help')
@bot.tree.command(name="help", description="Get a list of commands and features", guild=GUILD_ID)
async def help_command(interaction: Interaction):
    """
        Responds to the /help command with a list of available bot functionalities.

        This function:
        1. Removes the default help command.
        2. Registers a new slash command named "help".
        3. When called, sends an ephemeral message with bot information and available commands.

        Args:
           interaction (Interaction): The interaction object representing the command invocation.

        Note:
           The command is guild-specific, as defined by GUILD_ID.
        """
    print("/help called")
    multiline = ("### :triangular_flag_on_post: **HELP**\n" +
                 "Hello I am AI powered bot who will help you with everything about World of Tanks game and universe :smiley:\n" +
                 "These are my functionalities:\n"
                 "- /wot (message) :arrow_right: for general talk (tanks, equipment, tactics...)\n"
                 "- /map :arrow_right: for map guides"
                 )
    await interaction.response.send_message(multiline, ephemeral=True)


@bot.tree.command(name="wot", description="Chat about World of Tanks", guild=GUILD_ID)
@app_commands.describe(query="Your query related to World of Tanks")
async def wot_command(interaction: Interaction, query: str):
    """
        Handles the /wot slash command for World of Tanks related queries.

        This function:
        1. Defers the interaction response.
        2. Queries a model with the user's input.
        3. Sends the response back to the user.

        Args:
            interaction (Interaction): The interaction object from Discord.
            query (str): The user's World of Tanks related query.

        Note:
            - The command is guild-specific (GUILD_ID).
            - Responses are sent as ephemeral messages.
            - Uses split_send() to handle potentially long responses.
        """
    print("/wot called")
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
    except discord.errors.NotFound:
        print("Interaction not found - may be be reinitialized automatically possible discord API issue")
    rag_response = model.query(query, interaction.user.id)
    await split_send(rag_response, interaction)


@bot.tree.command(name="map", description="Get guides for maps", guild=GUILD_ID)
async def map_command(interaction: Interaction):
    """
       Handles the /map slash command to provide map guides.

       This function:
       1. Creates a DropdownView for map selection.
       2. Sends an ephemeral message with the dropdown.

       Args:
           interaction (Interaction): The interaction object from Discord.

       Note:
           - The command is guild-specific (GUILD_ID).
           - Uses DropdownView for map selection.
           - Handles potential Discord API issues.
       """
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
    """
        Handles the /player-stats slash command to provide personalized gameplay advice.

        This function:
        1. Defers the interaction response.
        2. Queries a model with the player's nickname for personalized advice.
        3. Sends the response back to the user.

        Args:
            interaction (Interaction): The interaction object from Discord.
            nickname (str): The player's in-game nickname.

        Note:
            - The command is guild-specific (GUILD_ID).
            - Responses are sent as ephemeral messages.
            - Uses split_send() to handle potentially long responses.
            - Handles potential Discord API issues.
        """
    print("/player-stats called")
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
    except discord.errors.NotFound:
        print("Interaction not found - may be be reinitialized automatically possible discord API issue")
    rag_response = model.player_query(nickname, interaction.user.id)
    await split_send(rag_response, interaction)


# Starts the Discord bot using the API key stored in the DISCORD_API_KEY environment variable.
# This should be the last line of the script as it starts the bot's event loop.
try:
    bot.run(os.environ.get("DISCORD_API_KEY"))
except TypeError as e:
    print("Failed to login - check your DISCORD_API_KEY")
    print(e)
