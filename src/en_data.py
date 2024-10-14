import numpy
from en_fontmap import normal_fontmap, bold_fontmap
from font import palette_transfer, char_dataset

### minimal sets of chars that can be useful in general
lower_alpha = set("abcdefghijklmnopqrstuvwxyz")
upper_alpha = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
alphabet = lower_alpha | upper_alpha
numbers = set("0123456789")
# for reference these are punctuation marks that exist in the font file
# $ ! ? , . • / ‘ ’ “ ” „ « » ( ) ♂ ♀ + - * # = & ~ : ;
# note: ellipsis … may not be used in english version of game


locations_palette = [
    numpy.array([0xFF, 0xFF, 0xFF], dtype=numpy.uint8),
    numpy.array([0xA3, 0x92, 0x92], dtype=numpy.uint8),
    numpy.array([0x01, 0x01, 0x01], dtype=numpy.uint8),
    numpy.array([0x00, 0x00, 0x00], dtype=numpy.uint8),  # used for bold
]
locations_charset = alphabet | numbers | set("’")
locations_chardata: char_dataset = palette_transfer(
    locations_charset,
    normal_fontmap,
    locations_palette,
)

dialog_palette = [
    numpy.array([0xFD, 0xFD, 0xFD], dtype=numpy.uint8),
    numpy.array([0xAA, 0xA2, 0xA2], dtype=numpy.uint8),
    numpy.array([0x59, 0x51, 0x51], dtype=numpy.uint8),
    numpy.array([0x00, 0x00, 0x00], dtype=numpy.uint8),  # used for bold
]
dialog_charset = alphabet | numbers | set("é’-&♂♀")
dialog_chardata: char_dataset = palette_transfer(
    dialog_charset,
    normal_fontmap,
    locations_palette,
)

species_palette = [
    numpy.array([0x59, 0x71, 0x69], dtype=numpy.uint8),
    numpy.array([0x28, 0x30, 0x28], dtype=numpy.uint8),
    numpy.array([0xFD, 0xFD, 0xFD], dtype=numpy.uint8),
    numpy.array([0xFF, 0xFF, 0xFF], dtype=numpy.uint8),  # used for bold
]
species_charset = alphabet | numbers | set("é’-&♂♀")
species_chardata: char_dataset = palette_transfer(
    species_charset,
    normal_fontmap,
    species_palette,
)

if not dialog_charset.issuperset(species_charset):
    print("dialog charset needs to contain all characters in the species charset")
    # because we use the dialog box to autotrack nicknames
    raise SystemExit


# something that uses bold_fontmap (like level, gender)
# etc ...

display_palette = locations_palette  # borrowing this palette
display_charset = alphabet | numbers | set("é’-(),♂♀")  # some additional punctuation
display_chardata = palette_transfer(
    display_charset,
    normal_fontmap,
    display_palette,
)

# TODO json-ify the long lists that don't need to be loaded for the full duration
# of the program and use some kind of context manager `with <context>:`


# consider splitting this so D/P/PT and HG/SS are separate and require less memory
class valids:
    """mainly for validation of recognized text"""

    # TODO verify all locations reachable in-game are detected properly
    locations = set(
        [
            "Mystery Zone",
            "Twinleaf Town",
            "Sandgem Town",
            "Floaroma Town",
            "Solaceon Town",
            "Celestic Town",
            "Jubilife City",
            "Canalave City",
            "Oreburgh City",
            "Eterna City",
            "Hearthome City",
            "Pastoria City",
            "Veilstone City",
            "Sunyshore City",
            "Snowpoint City",
            "Pokemon League",
            "Route 201",
            "Route 202",
            "Route 203",
            "Route 204",
            "Route 205",
            "Route 206",
            "Route 207",
            "Route 208",
            "Route 209",
            "Route 210",
            "Route 211",
            "Route 212",
            "Route 213",
            "Route 214",
            "Route 215",
            "Route 216",
            "Route 217",
            "Route 218",
            "Route 219",
            "Route 220",
            "Route 221",
            "Route 222",
            "Route 223",
            "Route 224",
            "Route 225",
            "Route 226",
            "Route 227",
            "Route 228",
            "Route 229",
            "Route 230",
            "Oreburgh Mine",
            "Valley Windworks",
            "Eterna Forest",
            "Fuego Ironworks",
            "Mt Coronet",
            "Spear Pillar",
            "Great Marsh",
            "Solaceon Ruins",
            "Victory Road",
            "Pal Park",
            "Amity Square",
            "Ravaged Path",
            "Floaroma Meadow",
            "Oreburgh Gate",
            "Fullmoon Island",
            "Sendoff Spring",
            "Turnback Cave",
            "Flower Paradise",
            "Snowpoint Temple",
            "Wayward Cave",
            "Ruin Maniac Cave",
            "Maniac Tunnel",
            "Trophy Garden",
            "Iron Island",
            "Old Chateau",
            "Galactic HQ",
            "Verity Lakefront",
            "Valor Lakefront",
            "Acuity Lakefront",
            "Spring Path",
            "Lake Verity",
            "Lake Valor",
            "Lake Acuity",
            "Newmoon Island",
            "Battle Tower",
            "Fight Area",
            "Survival Area",
            "Resort Area",
            "Stark Mountain",
            "Seabreak Path",
            "Hall of Origin",
            "Verity Cavern",
            "Valor Cavern",
            "Acuity Cavern",
            "Jubilife TV",
            "Poketch Co",
            "GTS",  # not sure if this shows up
            "Trainers’ School",
            "Mining Museum",
            "Flower Shop",
            "Cycle Shop",
            "Contest Hall",
            "Poffin House",
            "Foreign Building",
            "Pokemon Day Care",
            "Veilstone Store",
            "Game Corner",
            "Canalave Library",
            "Vista Lighthouse",
            "Sunyshore Market",
            "Pokemon Mansion",
            "Footstep House",
            "Cafe",
            "Grand Lake",
            "Restaurant",
            "Battle Park",
            "Battle Frontier",
            "Battle Factory",
            "Battle Castle",
            "Battle Arcade",
            "Battle Hall",
            "Distortion World",
            "Global Terminal",  # not sure if this shows up
            "Villa",  # not sure what this is
            "Battleground",  # not sure what this is
            "ROTOM’s Room",  # this shouldn't even show up
            "T G Eterna Bldg",  # this shouldn't even show up
            "Iron Ruins",
            "Iceberg Ruins",
            "Rock Peak Ruins",
            "New Bark Town",
            "Cherrygrove City",
            "Violet City",
            "Azalea Town",
            "Cianwood City",
            "Goldenrod City",
            "Olivine City",
            "Ecruteak City",
            "Mahogany Town",
            "Lake of Rage",
            "Blackthorn City",
            "Mt Silver",
            "Pallet Town",
            "Viridian City",
            "Pewter City",
            "Cerulean City",
            "Lavender Town",
            "Vermilion City",
            "Celadon City",
            "Fuchsia City",
            "Cinnabar Island",
            "Indigo Plateau",
            "Saffron City",
            "Route 1",
            "Route 2",
            "Route 3",
            "Route 4",
            "Route 5",
            "Route 6",
            "Route 7",
            "Route 8",
            "Route 9",
            "Route 10",
            "Route 11",
            "Route 12",
            "Route 13",
            "Route 14",
            "Route 15",
            "Route 16",
            "Route 17",
            "Route 18",
            "Route 19",
            "Route 20",
            "Route 21",
            "Route 22",
            "Route 23",
            "Route 24",
            "Route 25",
            "Route 26",
            "Route 27",
            "Route 28",
            "Route 29",
            "Route 30",
            "Route 31",
            "Route 32",
            "Route 33",
            "Route 34",
            "Route 35",
            "Route 36",
            "Route 37",
            "Route 38",
            "Route 39",
            "Route 40",
            "Route 41",
            "Route 42",
            "Route 43",
            "Route 44",
            "Route 45",
            "Route 46",
            "Route 47",
            "Route 48",
            "DIGLETT’s Cave",  # this may be wrong depending on randomizer settings
            "Mt Moon",
            "Cerulean Cave",
            "Rock Tunnel",
            "Power Plant",
            "Safari Zone",
            "Seafoam Islands",
            "Sprout Tower",
            "Bell Tower",
            "Burned Tower",
            "National Park",
            "Radio Tower",
            "Ruins of Alph",
            "Union Cave",
            "SLOWPOKE Well",  # this may be wrong depending on randomizer settings
            "Lighthouse",
            "Team Rocket HQ",
            "Ilex Forest",
            "Goldenrod Tunnel",
            "Mt Mortar",
            "Ice Path",
            "Whirl Islands",
            "Mt Silver Cave",
            "Dark Cave",
            "Victory Road",
            "Dragon’s Den",
            "Tohjo Falls",
            "Viridian Forest",
            "Pokeathlon Dome",
            "S S Aqua",
            "Safari Zone Gate",
            "Cliff Cave",
            "Frontier Access",
            "Bellchime Trail",
            "Sinjoh Ruins",
            "Embedded Tower",
            "Pokewalker",
            "Cliff Edge Gate",
        ]
    )

    # TODO verify all species are detected properly
    species = set(
        [
            "Bulbasaur",
            "Ivysaur",
            "Venusaur",
            "Charmander",
            "Charmeleon",
            "Charizard",
            "Squirtle",
            "Wartortle",
            "Blastoise",
            "Caterpie",
            "Metapod",
            "Butterfree",
            "Weedle",
            "Kakuna",
            "Beedrill",
            "Pidgey",
            "Pidgeotto",
            "Pidgeot",
            "Rattata",
            "Raticate",
            "Spearow",
            "Fearow",
            "Ekans",
            "Arbok",
            "Pikachu",
            "Raichu",
            "Sandshrew",
            "Sandslash",
            "Nidoran♀",
            "Nidorina",
            "Nidoqueen",
            "Nidoran♂",
            "Nidorino",
            "Nidoking",
            "Clefairy",
            "Clefable",
            "Vulpix",
            "Ninetales",
            "Jigglypuff",
            "Wigglytuff",
            "Zubat",
            "Golbat",
            "Oddish",
            "Gloom",
            "Vileplume",
            "Paras",
            "Parasect",
            "Venonat",
            "Venomoth",
            "Diglett",
            "Dugtrio",
            "Meowth",
            "Persian",
            "Psyduck",
            "Golduck",
            "Mankey",
            "Primeape",
            "Growlithe",
            "Arcanine",
            "Poliwag",
            "Poliwhirl",
            "Poliwrath",
            "Abra",
            "Kadabra",
            "Alakazam",
            "Machop",
            "Machoke",
            "Machamp",
            "Bellsprout",
            "Weepinbell",
            "Victreebel",
            "Tentacool",
            "Tentacruel",
            "Geodude",
            "Graveler",
            "Golem",
            "Ponyta",
            "Rapidash",
            "Slowpoke",
            "Slowbro",
            "Magnemite",
            "Magneton",
            "Farfetch’d",
            "Doduo",
            "Dodrio",
            "Seel",
            "Dewgong",
            "Grimer",
            "Muk",
            "Shellder",
            "Cloyster",
            "Gastly",
            "Haunter",
            "Gengar",
            "Onix",
            "Drowzee",
            "Hypno",
            "Krabby",
            "Kingler",
            "Voltorb",
            "Electrode",
            "Exeggcute",
            "Exeggutor",
            "Cubone",
            "Marowak",
            "Hitmonlee",
            "Hitmonchan",
            "Lickitung",
            "Koffing",
            "Weezing",
            "Rhyhorn",
            "Rhydon",
            "Chansey",
            "Tangela",
            "Kangaskhan",
            "Horsea",
            "Seadra",
            "Goldeen",
            "Seaking",
            "Staryu",
            "Starmie",
            "Mr Mime",
            "Scyther",
            "Jynx",
            "Electabuzz",
            "Magmar",
            "Pinsir",
            "Tauros",
            "Magikarp",
            "Gyarados",
            "Lapras",
            "Ditto",
            "Eevee",
            "Vaporeon",
            "Jolteon",
            "Flareon",
            "Porygon",
            "Omanyte",
            "Omastar",
            "Kabuto",
            "Kabutops",
            "Aerodactyl",
            "Snorlax",
            "Articuno",
            "Zapdos",
            "Moltres",
            "Dratini",
            "Dragonair",
            "Dragonite",
            "Mewtwo",
            "Mew",
            "Chikorita",
            "Bayleef",
            "Meganium",
            "Cyndaquil",
            "Quilava",
            "Typhlosion",
            "Totodile",
            "Croconaw",
            "Feraligatr",
            "Sentret",
            "Furret",
            "Hoothoot",
            "Noctowl",
            "Ledyba",
            "Ledian",
            "Spinarak",
            "Ariados",
            "Crobat",
            "Chinchou",
            "Lanturn",
            "Pichu",
            "Cleffa",
            "Igglybuff",
            "Togepi",
            "Togetic",
            "Natu",
            "Xatu",
            "Mareep",
            "Flaaffy",
            "Ampharos",
            "Bellossom",
            "Marill",
            "Azumarill",
            "Sudowoodo",
            "Politoed",
            "Hoppip",
            "Skiploom",
            "Jumpluff",
            "Aipom",
            "Sunkern",
            "Sunflora",
            "Yanma",
            "Wooper",
            "Quagsire",
            "Espeon",
            "Umbreon",
            "Murkrow",
            "Slowking",
            "Misdreavus",
            "Unown",
            "Wobbuffet",
            "Girafarig",
            "Pineco",
            "Forretress",
            "Dunsparce",
            "Gligar",
            "Steelix",
            "Snubbull",
            "Granbull",
            "Qwilfish",
            "Scizor",
            "Shuckle",
            "Heracross",
            "Sneasel",
            "Teddiursa",
            "Ursaring",
            "Slugma",
            "Magcargo",
            "Swinub",
            "Piloswine",
            "Corsola",
            "Remoraid",
            "Octillery",
            "Delibird",
            "Mantine",
            "Skarmory",
            "Houndour",
            "Houndoom",
            "Kingdra",
            "Phanpy",
            "Donphan",
            "Porygon2",
            "Stantler",
            "Smeargle",
            "Tyrogue",
            "Hitmontop",
            "Smoochum",
            "Elekid",
            "Magby",
            "Miltank",
            "Blissey",
            "Raikou",
            "Entei",
            "Suicune",
            "Larvitar",
            "Pupitar",
            "Tyranitar",
            "Lugia",
            "Ho-Oh",
            "Celebi",
            "Treecko",
            "Grovyle",
            "Sceptile",
            "Torchic",
            "Combusken",
            "Blaziken",
            "Mudkip",
            "Marshtomp",
            "Swampert",
            "Poochyena",
            "Mightyena",
            "Zigzagoon",
            "Linoone",
            "Wurmple",
            "Silcoon",
            "Beautifly",
            "Cascoon",
            "Dustox",
            "Lotad",
            "Lombre",
            "Ludicolo",
            "Seedot",
            "Nuzleaf",
            "Shiftry",
            "Taillow",
            "Swellow",
            "Wingull",
            "Pelipper",
            "Ralts",
            "Kirlia",
            "Gardevoir",
            "Surskit",
            "Masquerain",
            "Shroomish",
            "Breloom",
            "Slakoth",
            "Vigoroth",
            "Slaking",
            "Nincada",
            "Ninjask",
            "Shedinja",
            "Whismur",
            "Loudred",
            "Exploud",
            "Makuhita",
            "Hariyama",
            "Azurill",
            "Nosepass",
            "Skitty",
            "Delcatty",
            "Sableye",
            "Mawile",
            "Aron",
            "Lairon",
            "Aggron",
            "Meditite",
            "Medicham",
            "Electrike",
            "Manectric",
            "Plusle",
            "Minun",
            "Volbeat",
            "Illumise",
            "Roselia",
            "Gulpin",
            "Swalot",
            "Carvanha",
            "Sharpedo",
            "Wailmer",
            "Wailord",
            "Numel",
            "Camerupt",
            "Torkoal",
            "Spoink",
            "Grumpig",
            "Spinda",
            "Trapinch",
            "Vibrava",
            "Flygon",
            "Cacnea",
            "Cacturne",
            "Swablu",
            "Altaria",
            "Zangoose",
            "Seviper",
            "Lunatone",
            "Solrock",
            "Barboach",
            "Whiscash",
            "Corphish",
            "Crawdaunt",
            "Baltoy",
            "Claydol",
            "Lileep",
            "Cradily",
            "Anorith",
            "Armaldo",
            "Feebas",
            "Milotic",
            "Castform",
            "Kecleon",
            "Shuppet",
            "Banette",
            "Duskull",
            "Dusclops",
            "Tropius",
            "Chimecho",
            "Absol",
            "Wynaut",
            "Snorunt",
            "Glalie",
            "Spheal",
            "Sealeo",
            "Walrein",
            "Clamperl",
            "Huntail",
            "Gorebyss",
            "Relicanth",
            "Luvdisc",
            "Bagon",
            "Shelgon",
            "Salamence",
            "Beldum",
            "Metang",
            "Metagross",
            "Regirock",
            "Regice",
            "Registeel",
            "Latias",
            "Latios",
            "Kyogre",
            "Groudon",
            "Rayquaza",
            "Jirachi",
            "Deoxys",
            "Turtwig",
            "Grotle",
            "Torterra",
            "Chimchar",
            "Monferno",
            "Infernape",
            "Piplup",
            "Prinplup",
            "Empoleon",
            "Starly",
            "Staravia",
            "Staraptor",
            "Bidoof",
            "Bibarel",
            "Kricketot",
            "Kricketune",
            "Shinx",
            "Luxio",
            "Luxray",
            "Budew",
            "Roserade",
            "Cranidos",
            "Rampardos",
            "Shieldon",
            "Bastiodon",
            "Burmy",
            "Wormadam",
            "Mothim",
            "Combee",
            "Vespiquen",
            "Pachirisu",
            "Buizel",
            "Floatzel",
            "Cherubi",
            "Cherrim",
            "Shellos",
            "Gastrodon",
            "Ambipom",
            "Drifloon",
            "Drifblim",
            "Buneary",
            "Lopunny",
            "Mismagius",
            "Honchkrow",
            "Glameow",
            "Purugly",
            "Chingling",
            "Stunky",
            "Skuntank",
            "Bronzor",
            "Bronzong",
            "Bonsly",
            "Mime Jr",
            "Happiny",
            "Chatot",
            "Spiritomb",
            "Gible",
            "Gabite",
            "Garchomp",
            "Munchlax",
            "Riolu",
            "Lucario",
            "Hippopotas",
            "Hippowdon",
            "Skorupi",
            "Drapion",
            "Croagunk",
            "Toxicroak",
            "Carnivine",
            "Finneon",
            "Lumineon",
            "Mantyke",
            "Snover",
            "Abomasnow",
            "Weavile",
            "Magnezone",
            "Lickilicky",
            "Rhyperior",
            "Tangrowth",
            "Electivire",
            "Magmortar",
            "Togekiss",
            "Yanmega",
            "Leafeon",
            "Glaceon",
            "Gliscor",
            "Mamoswine",
            "Porygon-Z",
            "Gallade",
            "Probopass",
            "Dusknoir",
            "Froslass",
            "Rotom",
            "Uxie",
            "Mesprit",
            "Azelf",
            "Dialga",
            "Palkia",
            "Heatran",
            "Regigigas",
            "Giratina",
            "Cresselia",
            "Phione",
            "Manaphy",
            "Darkrai",
            "Shaymin",
            "Arceus",
        ]
    )
