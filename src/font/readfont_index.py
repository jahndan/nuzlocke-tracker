from bidict import bidict, ValueDuplicationError


def prefix(prefix: str, elem: str | None):
    return None if elem == None else f"{prefix}{elem}"


"""
each data file holds font data in 32 rows of 16 sections of character data
each section is 16px•16px and corresponds to a character in the mapping below

this mapping is not complete, but it does not necessarily need to be--many
symbols included in the font file are not required to be recognized for
nuzlocke tracking logic

so far we've only mapped the symbols that are likely to be used to do the
logic for the english versions, but anyone may contribute in the future to
add support for other localizations

(note that while some diacritics are used in the english versions, they don't
meaningfully distinguish words that appear in the games from others, so there
is no requirement to recognize that separately)
"""

"""
note about prefixes:
many symbols have two versions used in different localizations of the game,
so they need a prefix to differentiate the versions:
- jp is used as a prefix for symbols that are specifically sized and spaced
  for typesetting the japanese versions
- en is used as a prefix for symbols that are sized and spaced for the font
  used in the international versions of the game (not all of them are in the
  english versions but nearly all of them are, so I used that prefix)
- no prefix is given to symbols that are used in all versions of the game,
  which are generally not displayed among other text symbols, but isolated.
most non-text symbols have a version sized for the japanese typesetting, so
those should have the appropriate prefix
"""

# normal font data (used almost everywhere)
data_0 = [
    element  # auto-flattened for convenience
    for sublist in [  # but formatted so the rows are still delineated nicely
        [
            # this section roughly corresponds to the japanese font
            "",  # whitespace
            # jp-hiragana
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            # jp-katakana
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            # jp-numerals (these are spaced/sized to match the rest of the jp font)
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            # jp-uppercase latin characters (these are spaced/sized to match the rest of the jp font)
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            # jp-lowercase latin characters (these are spaced/sized to match the rest of the jp font)
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            None,  # no character data here
        ],
        [
            # jp-punctuation (these are spaced/sized to match the rest of the jp font)
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            # jp-miscellaneous
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",  # japanese symbol for pokedollar?
            # symbols used in in-game UI
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        # this section roughly corresponds to the international font
        [
            # numerals
            "en.zero",
            "en.one",
            "en.two",
            "en.three",
            "en.four",
            "en.five",
            "en.six",
            "en.seven",
            "en.eight",
            "en.nine",
            # uppercase latin characters
            "en.upper_a",
            "en.upper_b",
            "en.upper_c",
            "en.upper_d",
            "en.upper_e",
            "en.upper_f",
        ],
        [
            "en.upper_g",
            "en.upper_h",
            "en.upper_i",
            "en.upper_j",
            "en.upper_k",
            "en.upper_l",
            "en.upper_m",
            "en.upper_n",
            "en.upper_o",
            "en.upper_p",
            "en.upper_q",
            "en.upper_r",
            "en.upper_s",
            "en.upper_t",
            "en.upper_u",
            "en.upper_v",
        ],
        [
            "en.upper_w",
            "en.upper_x",
            "en.upper_y",
            "en.upper_z",
            # lowercase latin characters
            "en.lower_a",
            "en.lower_b",
            "en.lower_c",
            "en.lower_d",
            "en.lower_e",
            "en.lower_f",
            "en.lower_g",
            "en.lower_h",
            "en.lower_i",
            "en.lower_j",
            "en.lower_k",
            "en.lower_l",
        ],
        [
            "en.lower_m",
            "en.lower_n",
            "en.lower_o",
            "en.lower_p",
            "en.lower_q",
            "en.lower_r",
            "en.lower_s",
            "en.lower_t",
            "en.lower_u",
            "en.lower_v",
            "en.lower_w",
            "en.lower_x",
            "en.lower_y",
            "en.lower_z",
            # vowel variations with diacritics
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "en.cross",  # multiplication symbol ×
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "en.divide",  # division symbol ÷
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "en.pokemoney",  # pokédollar symbol
            "",
            "",
            "en.exclaim",  # exclamation mark
            "en.question",  # question mark
            "en.comma",
            "en.period",  # full stop
            "en.ellipsis",  # ...
            "en.dot",  # interpunct •
        ],
        [
            "en.slash",  # forward slash /
            "en.osquote",  # opening single quote
            "en.csquote",  # closing single quote
            "en.odquote",  # opening double quote
            "en.cdquote",  # closing double quote
            "",
            "",
            "",
            "en.oparen",  # opening parenthesis
            "en.cparen",  # closing parenthesis
            "en.male",  # ♂
            "en.female",  # ♀
            "en.plus",
            "en.dash",  # minus, but likely used in dialogue as dash
            "en.asterisk",
            "en.hash",  # pound symbol #
        ],
        [
            "en.equal",
            "en.ampersand",  # and symbol
            "en.tilde",  # negation ~
            "en.colon",
            "en.semicolon",
            # playing card suits
            "en.spade",
            "en.club",
            "en.heart",
            "en.diamond",
            # miscellaneous shapes
            "en.star",  # 5 point star
            "en.target",  # might be coins
            "en.circle",
            "en.square",
            "en.triangle",
            "en.rhombus",  # diagonal square
            # other symbols
            "en.address",  # at symbol @
        ],
        [
            "en.note",  # musical note
            "en.percent",
            "",
            "",
            "",
            "",
            # emotes
            "en.smile",
            "en.happy",
            "en.cry",
            "en.angry",
            "",
            "",
            "",
            "",
            "",
            "en.poke",  # PK
        ],
        [
            "en.mon",  # MN
            # more whitespace
            "",
            "",
            "",
            "",
            "",
            "",
            # no more character data below
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
    ]
    for element in sublist
]

if __name__ == "__main__":
    print("\033[1mdata_0\033[0m")
    print(data_0)
    print()

# bold font data (mostly only used in battle)
data_2 = [
    (
        # identical layout to normal font but without some symbols
        (prefix("b_", data_0[i]) if data_0[i] != "" else "")
        if i
        not in set(
            j
            for j in range((2 + 17 * 16), (15 + 17 * 16))
            if j not in range((10 + 17 * 16), (14 + 17 * 16))
        )
        else None
    )
    for i in range(len(data_0))
]

if __name__ == "__main__":
    print("\033[1mdata_2\033[0m")
    print(data_2)
    print()

"""a bijective mapping between font file partition index and exported filename"""
normal_fontmap = bidict()
# mapping index <--> names but only add them if name != "" and name  != None
for i in range(len(data_0)):
    if data_0[i] != None:  # no character data
        if data_0[i] != "":  # currently unlabeled
            try:
                normal_fontmap[i] = data_0[i]
            except ValueDuplicationError:
                print(f"Duplicate character filename found in normal_fontmap at {i}")

if __name__ == "__main__":
    print("\033[1mnormal_fontmap\033[0m")
    print(normal_fontmap)
    print()

"""a bijective mapping between font file partition index and exported filename"""
bold_fontmap = bidict()
# mapping index <--> names but only add them if name != "" and name  != None
for i in range(len(data_2)):
    if data_2[i] != None:  # no character data
        if data_2[i] != "":  # currently unlabeled
            try:
                bold_fontmap[i] = data_2[i]
            except ValueDuplicationError:
                print(f"Duplicate character filename found in bold_fontmap at {i}")

if __name__ == "__main__":
    print("\033[1mbold_fontmap\033[0m")
    print(bold_fontmap)
    print()

### NOTES
# only normal_fontmap and bold_fontmap are intended to be used (they map from indices to filenames, and
# don't strictly *need* to be bidicts, but conveniently, it raises errors when value duplications occur)
### TODO
# fill out character names according to fontfile layout (i.e. replace all placeholder "" with actual names)
# remove guards once names are filled in and finalized (if data == ""), (ValueDuplicationError)
