from bidict import (
    bidict,
    OnDup,
    RAISE,
    KeyDuplicationError,
    ValueDuplicationError,
)
from font.readfont_index import normal_data_0, bold_data_2
from common import reset, bold, FilenameNotFoundError, CharacterDataNotFoundError


# singular characters indexed in the same order as the font file
# when character is not necessary for logic in en_model, we store None
indexed_chars = [
    element  # auto-flattened for convenience
    for sublist in [  # but formatted so the rows are still delineated nicely
        # this section roughly corresponds to the japanese font
        [
            None,
            # jp hiragana
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
        [
            None,
            # jp katakana
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
        [
            None,
            # jp numerals (these are spaced/sized to match the rest of the jp font)
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
            # jp uppercase latin characters (these are spaced/sized to match the rest of the jp font)
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
        [
            None,
            None,
            None,
            None,
            None,
            # jp lowercase latin characters (these are spaced/sized to match the rest of the jp font)
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
            None,  # no character data here
        ],
        [
            # jp punctuation (these are spaced/sized to match the rest of the jp font)
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
            # jp miscellaneous
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
        [
            None,
            None,
            # symbols used in in-game UI (these shouldn't be necessary at all)
            ### requesting these will cause errors since the bold font does not include these characters
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
        # this section roughly corresponds to the international font
        [
            # numerals
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            # uppercase latin characters
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
        ],
        [
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
        ],
        [
            "W",
            "X",
            "Y",
            "Z",
            # lowercase latin characters
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
        ],
        [
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            # vowel variations with diacritics
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
        [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            "$",  # pokédollar symbol
            None,
            None,
            "!",
            "?",
            ",",
            ".",
            None,  ### I don't believe they use the actual ellipsis character in the english version
            "•",  # interpunct (dot)
        ],
        [
            "/",  # forward slash /
            "‘",  # opening single quote
            "’",  # closing single quote (presumably doubles as apostrophe)
            "“",  # opening double quote
            "”",  # closing double quote
            None,
            None,
            None,
            "(",  # opening parenthesis
            ")",  # closing parenthesis
            "♂",
            "♀",
            None,
            "-",  # likely used in dialogue as dash
            None,
            None,
        ],
        [
            None,
            "&",
            "~",
            ":",
            ";",
            # playing card suits
            None,
            None,
            None,
            None,
            # miscellaneous shapes
            None,
            None,
            None,
            None,
            None,
            None,
            # other symbols
            "@",  # at symbol @
        ],
        [
            None,
            "%",
            None,
            None,
            None,
            None,
            # emotes
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,  # PK
        ],
        [
            None,  # MN
            # more whitespace
            None,
            None,
            None,
            None,
            None,
            None,
            # new characters added in platinum
            None,
            ### requesting the underscores will also cause errors since the bold font does not include them
            None,  # underscore
            None,  # wide underscore
            # no more character data below
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
    print(f"{bold}indexed_chars{reset}")
    print(indexed_chars)
    print()

"""precise mapping between actual characters and normal font data (i.e. filenames)"""
normal_fontmap = bidict()
for i, x in enumerate(indexed_chars):
    if x is not None:  # unneeded (or invalid)
        try:
            if normal_data_0[i] == "":
                raise FilenameNotFoundError
            if normal_data_0[i] is None:
                raise CharacterDataNotFoundError
            normal_fontmap.put(x, normal_data_0[i], OnDup(key=RAISE, val=RAISE))
        except FilenameNotFoundError:
            print(
                f"Character {x} requested, but no corresponding filename found in data_0 at index {i}"
            )
        except CharacterDataNotFoundError:
            print(
                f"Character {x} requested, but no corresponding image data found in data_0 at index {i}"
            )
        except KeyDuplicationError:
            print(
                f"Duplicate character found in indexed_chars at {i}: {indexed_chars[i]}"
            )
        except ValueDuplicationError:
            print(
                f"Duplicate character filename found in data_0 at {i}: {normal_data_0[i]}"
            )

if __name__ == "__main__":
    print(f"{bold}normal_fontmap{reset}")
    print(normal_fontmap)
    print()

# note: we make the assumption that of the few characters that exist in the normal font,
# but not the bold font, none of them are needed for the tracker logic (and thus are not
# requested in the above list)

"""precise mapping between actual characters and bold font data (i.e. filenames)"""
bold_fontmap = bidict()
for i, x in enumerate(indexed_chars):
    if x is not None:  # unneeded (or invalid)
        try:
            if bold_data_2[i] == "":
                raise FilenameNotFoundError
            if bold_data_2[i] is None:
                raise CharacterDataNotFoundError
            bold_fontmap.put(x, bold_data_2[i], OnDup(key=RAISE, val=RAISE))
        except FilenameNotFoundError:
            print(
                f"Character {x} requested, but no corresponding filename found in data_2 at index {i}"
            )
        except CharacterDataNotFoundError:
            print(
                f"Character {x} requested, but no corresponding image data found in data_2 at index {i}"
            )
        except KeyDuplicationError:
            print(
                f"Duplicate character found in indexed_chars at {i}: {indexed_chars[i]}"
            )
        except ValueDuplicationError:
            print(
                f"Duplicate character filename found in data_2 at {i}: {bold_data_2[i]}"
            )

if __name__ == "__main__":
    print(f"{bold}bold_fontmap{reset}")
    print(bold_fontmap)
    print()
