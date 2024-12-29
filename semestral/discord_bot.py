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
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.edit_message(interaction.message.id, content="Thinking...", view=None)

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

        # TODO
        query = f"How should I play the map: {map_name} with each tank class?"
        rag_response = model.query(query, interaction.user.id)
        await split_send(rag_response, interaction, file=file, embed=embed)


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
    await interaction.response.defer(ephemeral=True)
    if (time.time() - last_prompt_time) >= 5:
        last_prompt_time = time.time()
        print("!wot called")
        rag_response = model.query(query, interaction)
        rag_response2 = """Odkudsi z konce ulièky se linula vùnì praené kávy - pravé kávy, ne Kávy
vítìzství. Winston se bezdìènì zastavil. Snad na dvì vteøiny se zase octl
v polozapomenutém svìtì dìtství. Vtom bouchly dveøe a odøízly tu vùni
tak prudce, jako by to byl prchavý zvuk.
Uel nìkolik kilometrù po chodnících a v bércovém vøedu mu cukalo. U
po druhé za tøi týdny vynechal veèer ve Spoleèenském støedisku; byl to
nepøedloený èin, protoe èlovìk si mohl být jist, e poèet jeho návtìv ve
Støedisku se bedlivì zaznamenává. V zásadì nemìl èlen Strany nikdy volno a
nebyl nikdy sám, jedinì v posteli. Pøedpokládalo se, e pokud právì nepracuje,
nejí nebo nespí, úèastní se nìjaké spoleèné zábavy; dìlat cokoli, co by jen
pøipomínalo touhu po samotì, tøeba jít sám na procházku, bylo vdy ponìkud
riskantní. V newspeaku pro to bylo slovo, jmenovalo se to ownlife, vlastní ivot,
a znamenalo to individualismus a výstøednost. Ale kdy dnes veèer vyel
z Ministerstva, voòavý dubnový vzduch ho zlákal. Obloha byla teple modrá, víc
ne jindy toho roku, a najednou mu ten dlouhý, hluèný veèer ve Støedisku, nudné,
vyèerpávající hry, pøednáky a halasné kamarádství podmazané ginem pøipadaly
nesnesitelné. Z náhlého popudu odboèil od autobusové zastávky a ponoøil se do
bluditì Londýna, nejdøív na jih, potom na východ, pak zase na sever, ztratil se
v neznámých ulicích a ani se nestaral, kterým smìrem jde.
Jestli je nìjaká nadìje, zapsal si do deníku, pak spoèívá v prolétech. Ta
slova se mu stále vracela jako výrok tajemné pravdy a zjevné absurdity. Octl se
mezi oumìlými, zalými brlohy hnìdé barvy severovýchodnì od nìkdejího
nádraí Saint Pancras. Kráèel dládìnou ulièkou poschoïových domkù
s otluèenými vraty, která se otvírala pøímo na chodník a zvlátním zpùsobem
pøipomínala krysí díry. Tu a tam stály mezi dladicemi kalue pinavé vody. Dovnitø
a ven tmavými vchody a boèními ulièkami, které ústily z obou stran ulice, proudilo
úasné mnoství lidí - dívky v plném kvìtu s hrubì nalíèenými rty, mladíci, kteøí
se vìeli dìvèatùm na paty, a nakynuté kolébající se eny, prozrazující, jak budou
ty dívky vypadat za deset let, staré shrbené bytosti, ourající se s nohama od
sebe, a otrhané bosé dìti, které si hrály v kaluích a rozprchly se pokadé, kdy
na nì matky rozhnìvanì zavolaly. Asi ètvrtina oken v ulici byla rozbitá a zatluèená
prkny. Lidé vìtinou nevìnovali Winstonovi pozornost; nìkteøí na nìho hledìli
s ostraitou zvìdavostí. Dvì obrovité eny s cihlovì èerveným pøedloktím,
sloeným na zástìøe, se bavily na zápraí. Jak se k nim blíil, zachytil Winston
útrky rozhovoru.
To je vecko hezký, øíkám jí. Ále kdybys byla na mým místì, udìlala bys to
jako já. To se lehko kritizuje, øíkám, ale ty nemá takový problémy co já.
Jo, øekla druhá, to je právì to. Zrovna tak to je.
Pronikavé hlasy najednou zmlkly. eny si ho prohlíely v nepøátelském tichu,
jak okolo nich procházel. Vlastnì to ani nebylo nepøátelství, jen jakási ostraitost,
- 52 -
náhlé strnutí, jako by se kolem proplazil chøestý. Modrá kombinéza Strany urèitì
nebyla na takové ulici èastým zjevem. Bylo vskutku nemoudré nechat se vidìt
v takových místech, pokud tam èlovìk nemìl konkrétnì co dìlat. Mohla by ho
zastavit hlídka, kdyby na ni narazil. Mohl byste nám ukázat doklady, soudruhu?
Co tu dìláte? V kolik hodin jste odeel z práce? Chodíte tudy pravidelnì domù?
a tak dále a tak dále. Ne e by existovalo nìjaké pravidlo zapovídající jít domù
neobvyklou cestou; ale kdy se o tom doslechla Ideopolicie, staèilo to, aby
èlovìk na sebe upozornil.
Najednou byla celá ulice v pohybu. Varovné výkøiky se ozývaly ze vech
stran. Lidé mizeli ve vratech jako králíci. Nìjaká mladá ena vybìhla ze vrat právì
pøed Winstonem, uchopila dìcko, které si hrálo v kalui, pøehodila pøes nì zástìru
a skoèila zpátky, to vechno jakoby jediným pohybem. V tom okamiku se vynoøil
z boèní ulièky jakýsi èlovìk v èerném pomaèkaném obleku, vybìhl smìrem
k Winstonovi a vzruenì ukazoval na oblohu.
Parník! køièel. Pozor, éfe! Rovnou nad hlavou! Rychle si lehnìte!
Parník byla pøezdívka, kterou proléti z neznámého dùvodu oznaèovali
raketové støely. Winston bez váhání padl na zem. Proléti mìli skoro vdycky
pravdu, kdy èlovìka takhle varovali. Jako by mìli estý smysl, který je upozornil
nìkolik sekund pøedtím, ne pøiletìla raketa, aèkoliv se prý rakety pohybovaly
rychleji ne zvuk. Winston si pøikryl hlavu rukama. Ozval se rachot, který zvedl
dlabu, sprka lehkých pøedmìtù se mu snesla na záda. Kdy vstal, zjistil, e je
pokryt úlomky skla z nejbliího okna.
el dál. Raketa zdemolovala skupinu domù o 200 metrù dál v ulici.
Chuchvalec èerného kouøe visel na obloze, nad zemí se vznáel oblak prachu,
v nìm se shromaïoval dav okolo trosek. Na dlabì pøed ním leela hromádka
omítky a uprostøed spatøil jasnì èervený pruh. Kdy pøistoupil blí, zjistil, e je to
lidská ruka uatá v zápìstí. Kromì krvavé rány byla ruka tak bílá, e pøipomínala
sádrový odlitek.
Odkopl tu vìc do pøíkopu a potom, aby se vyhnul davu, vykroèil doprava
boèní ulicí. Po tøech nebo ètyøech minutách opustil oblast, kterou zasáhla raketa.
Nuzný, mravenèí ivot v ulicích pokraèoval, jako by se nic nestalo. Bylo u skoro
dvacet hodin a výèepy, do kterých chodili proléti (øíkali jim hospody), byly
pøecpané zákazníky. Z jejich pinavých dvoukøídlých dveøí, které se bez ustání
otvíraly a zavíraly, vycházel zápach moèe, pilin a kyselého piva. V rohu, který
tvoøilo vyènívající prùèelí domu, stáli tìsnì u sebe tøi mui; prostøední drel sloené
noviny a druzí dva mu èetli pøes rameno. Jetì ne se pøiblíil natolik, aby z výrazu
jejich tváøí nìco vyrozumìl, poznal podle drení tìla, e jsou plnì soustøedìni.
Zøejmì èetli nìjakou závanou zprávu. Kdy byl na pár krokù od nich, skupina se
najednou rozpadla a dva mui se zaèali vánivì pøít. Chvíli to skoro vypadalo, e
se zaènou prát.
Nemùete, sakra, poslouchat, co vám øíkám? ádný èíslo se sedmièkou na
konci u ètrnáct mìsícù nevyhrálo."""
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
