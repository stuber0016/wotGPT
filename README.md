# wotGPT
================

**World of Tanks AI-Powered Discord Bot & Assistant**

### Table of Contents
-----------------

1. **[Overview](#overview)**
2. **[Features](#features)**
3. **[Dependencies & Requirements](#dependencies--requirements)**
4. **[Setup & Installation](#setup--installation)**
5. **[Usage](#usage)**
6. **[Commands Reference](#commands-reference)**
7. **[Development & Contribution](#development--contribution)**
8. **[License](#license)**

### Overview
------------

`wotGPT` is an innovative Discord bot designed specifically for the World of Tanks community. Leveraging cutting-edge AI
technology, this bot offers personalized gameplay advice, comprehensive map guides, and insightful responses to a wide
range of World of Tanks-related queries. Whether you're a seasoned tanker or just starting out, `wotGPT` is your
ultimate in-game companion.


### Features
------------

* **Personalized Advice**: Receive tailored tips based on your gameplay statistics.
* **Interactive Map Guides**: Engage with detailed map guides, complete with strategic insights for each tank class.
* **General Knowledge Base**: Query the bot on various World of Tanks topics, from tank specifications to game
  mechanics.
* **Real-Time Player Statistics**: Access up-to-the-minute player data, analyzed to provide actionable improvement
  strategies.

### Dependencies & Requirements
-----------------------------

* **Discord API Key**: Required for bot functionality.
* **Wargaming API Key**: Necessary for accessing player statistics and game data.
* **Hugging Face API Key (HFACE_API_KEY)**: For AI model interactions.
* **Python 3.x**: With `discord.py`, `dotenv`, `langchain`, and `requests` libraries.
* **Chroma Database**: Pre-built using the `rag_create.py` script.

### Setup & Installation
-----------------------

1. **Clone the Repository**:

```bash
git clone https://your-repo-url.com/wotGPT.git
```

2. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables**:
    * Create a `.env` file with your `DISCORD_API_KEY`, `WG_TANKOPEDIA`, `WG_SEARCH_PLAYER`, `WG_PLAYER_STAT`, and
      `HFACE_API_KEY`.
4. **Build Chroma Database (if not pre-existing)**:
    * Run `python rag_create.py` to generate the RAG context database.

### Usage
-----

1. **Invite the Bot to Your Discord Server** (using your `DISCORD_API_KEY`).
2. **Interact with the Bot**:
    * Use `/help` for command listings.
    * Engage with `/wot`, `/map`, `/player-stats` commands as per your needs.

### Commands Reference
--------------------

| **Command**     | **Description**                                        | **Usage**                       |
|-----------------|--------------------------------------------------------|---------------------------------|
| `/help`         | Displays available commands and features.              | `/help`                         |
| `/wot`          | General World of Tanks queries.                        | `/wot <your_query_here>`        |
| `/map`          | Interactive map guides.                                | `/map`                          |
| `/player-stats` | Personalized advice based on your gameplay statistics. | `/player-stats <your_nickname>` |

### Development & Contribution
-----------------------------

Contributions are welcome! Whether it's a bug fix, new feature, or documentation improvement, please:

1. Fork the repository.
2. Create a new branch (`git checkout -b your_branch_name`).
3. Make your changes and commit (`git commit -am "your_commit_message"`).
4. Push to the branch (`git push origin your_branch_name`).
5. Open a Pull Request.

**Sources**
====================

### **RAG Context Attribution and Source Disclosure**

#### **Origin of RAG Context**

The Retrieval-Augmented Generation (RAG) context utilized within the `wotGPT` project is derived from various sources
owned and operated by **Wargaming.net**:

* **Official World of Tanks Website** ([https://worldoftanks.com](https://worldoftanks.com))
    + Articles
    + Game guides
    + Informational pages
* **Wargaming.net Game Databases**
    + Accessible through publicly available APIs and web scraping (in accordance with Wargaming.net's terms of service)
    + Detailed game statistics
    + Tank specifications
    + Player information
* **World of Tanks Wiki** ([https://wiki.wargaming.net](https://wiki.wargaming.net))
    + Comprehensive, community-driven encyclopedia
    + In-depth information on game mechanics, tanks, maps, and more

Part of the RAG context is also inspired by tips from twitch streamer and
youtuber ([marty_vole](https://www.twitch.tv/marty_vole))

#### **Image Attribution**

Images incorporated into the RAG context:

* **Tank images**
* **Map overviews**
* **Gameplay screenshots**
  are sourced directly from Wargaming.net's official websites, game client, and affiliated platforms.

#### **License and Permission**

* **No explicit license** has been obtained from Wargaming.net for the use of their content in this project.
* **Fair use provisions** (where applicable) and the project's **non-commercial, educational nature** guide the
  incorporation of Wargaming.net's intellectual property.

#### **Disclaimer**

* The `wotGPT` project is **not officially affiliated** with Wargaming.net.
* The use of Wargaming.net's content is intended for the **betterment of the World of Tanks community**, through the
  provision of an innovative, AI-driven resource.

#### **Acknowledgment**

The `wotGPT` development team extends its **gratitude** to Wargaming.net for creating and maintaining the rich,
immersive world of World of Tanks, from which this project draws its foundational knowledge.

#### **UPDATE NOTICE**

This source chapter will be periodically reviewed to ensure compliance with any changes in Wargaming.net's:

* **Terms of service**
* **API usage policies**
* **Content licensing requirements**