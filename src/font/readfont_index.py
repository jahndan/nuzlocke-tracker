from bidict import bidict, ValueDuplicationError


def prefix(prefix: str, elem: str | None):
    return None if elem == None else f"{prefix}{elem}"


"""
each data file holds font data in 32 rows of 16 sections of character data
each section is 16px•16px and corresponds to a character in the mapping below

this mapping is not complete, but it does not necessarily need to be--many
symbols included in the font file are not required to be recognized for
nuzlocke tracking logic

I've transcribed most of the symbols in the fontfile (most of the remaining ones
are likely unnecessary for the english version), including most of the japanese
ones (no guarantee on any of it being correct--I don't speak japanese)

(note that while some diacritics are used in the english versions, they don't
meaningfully distinguish words that appear in the games from others, so there
is no requirement to recognize that separately for the english tracker logic)
"""

"""
note about prefixes:
many symbols have two versions used in different localizations of the game,
so they need a prefix to differentiate the versions:
- jp is used as a prefix for symbols that are specifically sized and spaced
  for typesetting the japanese versions (note: the filenames use kunrei-shiki
  spellings for disambiguation of kana that hepburn romanizes the same way)
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
        # this section roughly corresponds to the japanese font
        [
            "",  # whitespace
            # jp hiragana
            "jp.hiragana_small_a",  # ぁ
            "jp.hiragana_a",  # あ
            "jp.hiragana_small_i",  # ぃ
            "jp.hiragana_i",  # い
            "jp.hiragana_small_u",  # ぅ
            "jp.hiragana_u",  # う
            "jp.hiragana_small_e",  # ぇ
            "jp.hiragana_e",  # え
            "jp.hiragana_small_o",  # ぉ
            "jp.hiragana_o",  # お
            "jp.hiragana_ka",  # か
            "jp.hiragana_ga",  # が
            "jp.hiragana_ki",  # き
            "jp.hiragana_gi",  # ぎ
            "jp.hiragana_ku",  # く
        ],
        [
            "jp.hiragana_gu",  # ぐ
            "jp.hiragana_ke",  # け
            "jp.hiragana_ge",  # げ
            "jp.hiragana_ko",  # こ
            "jp.hiragana_go",  # ご
            "jp.hiragana_sa",  # さ
            "jp.hiragana_za",  # ざ
            "jp.hiragana_si",  # し
            "jp.hiragana_zi",  # じ
            "jp.hiragana_su",  # す
            "jp.hiragana_zu",  # ず
            "jp.hiragana_se",  # せ
            "jp.hiragana_ze",  # ぜ
            "jp.hiragana_so",  # そ
            "jp.hiragana_zo",  # ぞ
            "jp.hiragana_ta",  # た
        ],
        [
            "jp.hiragana_da",  # だ
            "jp.hiragana_ti",  # ち
            "jp.hiragana_di",  # ぢ
            "jp.hiragana_sokuon",  # っ
            "jp.hiragana_tu",  # つ
            "jp.hiragana_du",  # づ
            "jp.hiragana_te",  # て
            "jp.hiragana_de",  # で
            "jp.hiragana_to",  # と
            "jp.hiragana_do",  # ど
            "jp.hiragana_na",  # な
            "jp.hiragana_ni",  # に
            "jp.hiragana_nu",  # ぬ
            "jp.hiragana_ne",  # ね
            "jp.hiragana_no",  # の
            "jp.hiragana_ha",  # は
        ],
        [
            "jp.hiragana_ba",  # ば
            "jp.hiragana_pa",  # ぱ
            "jp.hiragana_hi",  # ひ
            "jp.hiragana_bi",  # び
            "jp.hiragana_pi",  # ぴ
            "jp.hiragana_fu",  # ふ
            "jp.hiragana_bu",  # ぶ
            "jp.hiragana_pu",  # ぷ
            "jp.hiragana_he",  # へ
            "jp.hiragana_be",  # べ
            "jp.hiragana_pe",  # ぺ
            "jp.hiragana_ho",  # ほ
            "jp.hiragana_bo",  # ぼ
            "jp.hiragana_po",  # ぽ
            "jp.hiragana_ma",  # ま
            "jp.hiragana_mi",  # み
        ],
        [
            "jp.hiragana_mu",  # む
            "jp.hiragana_me",  # め
            "jp.hiragana_mo",  # も
            "jp.hiragana_small_ya",  # ゃ
            "jp.hiragana_ya",  # や
            "jp.hiragana_small_yu",  # ゅ
            "jp.hiragana_yu",  # ゆ
            "jp.hiragana_small_yo",  # ょ
            "jp.hiragana_yo",  # よ
            "jp.hiragana_ra",  # ら
            "jp.hiragana_ri",  # り
            "jp.hiragana_ru",  # る
            "jp.hiragana_re",  # れ
            "jp.hiragana_ro",  # ろ
            "jp.hiragana_wa",  # わ
            "jp.hiragana_wo",  # を
        ],
        [
            "jp.hiragana_n",  # ん
            # jp katakana
            "jp.katakana_small_a",  # ァ
            "jp.katakana_a",  # ア
            "jp.katakana_small_i",  # ィ
            "jp.katakana_i",  # イ
            "jp.katakana_small_u",  # ゥ
            "jp.katakana_u",  # ウ
            "jp.katakana_small_e",  # ェ
            "jp.katakana_e",  # エ
            "jp.katakana_small_o",  # ォ
            "jp.katakana_o",  # オ
            "jp.katakana_ka",  # カ
            "jp.katakana_ga",  # ガ
            "jp.katakana_ki",  # キ
            "jp.katakana_gi",  # ギ
            "jp.katakana_ku",  # ク
        ],
        [
            "jp.katakana_gu",  # グ
            "jp.katakana_ke",  # ケ
            "jp.katakana_ge",  # ゲ
            "jp.katakana_ko",  # コ
            "jp.katakana_go",  # ゴ
            "jp.katakana_sa",  # サ
            "jp.katakana_za",  # ザ
            "jp.katakana_si",  # シ
            "jp.katakana_zi",  # ジ
            "jp.katakana_su",  # ス
            "jp.katakana_zu",  # ズ
            "jp.katakana_se",  # セ
            "jp.katakana_ze",  # ゼ
            "jp.katakana_so",  # ソ
            "jp.katakana_zo",  # ゾ
            "jp.katakana_ta",  # タ
        ],
        [
            "jp.katakana_da",  # ダ
            "jp.katakana_ti",  # チ
            "jp.katakana_di",  # ヂ
            "jp.katakana_sokuon",  # ッ
            "jp.katakana_tu",  # ツ
            "jp.katakana_du",  # ヅ
            "jp.katakana_te",  # テ
            "jp.katakana_de",  # デ
            "jp.katakana_to",  # ト
            "jp.katakana_do",  # ド
            "jp.katakana_na",  # ナ
            "jp.katakana_ni",  # ニ
            "jp.katakana_nu",  # ヌ
            "jp.katakana_ne",  # ネ
            "jp.katakana_no",  # ノ
            "jp.katakana_ha",  # ハ
        ],
        [
            "jp.katakana_ba",  # バ
            "jp.katakana_pa",  # パ
            "jp.katakana_hi",  # ヒ
            "jp.katakana_bi",  # ビ
            "jp.katakana_pi",  # ピ
            "jp.katakana_fu",  # フ
            "jp.katakana_bu",  # ブ
            "jp.katakana_pu",  # プ
            "jp.katakana_he",  # ヘ
            "jp.katakana_be",  # ベ
            "jp.katakana_pe",  # ペ
            "jp.katakana_ho",  # ホ
            "jp.katakana_bo",  # ボ
            "jp.katakana_po",  # ポ
            "jp.katakana_ma",  # マ
            "jp.katakana_mi",  # ミ
        ],
        [
            "jp.katakana_mu",  # ム
            "jp.katakana_me",  # メ
            "jp.katakana_mo",  # モ
            "jp.katakana_small_ya",  # ャ
            "jp.katakana_ya",  # ヤ
            "jp.katakana_small_yu",  # ュ
            "jp.katakana_yu",  # ユ
            "jp.katakana_small_yo",  # ョ
            "jp.katakana_yo",  # ヨ
            "jp.katakana_ra",  # ラ
            "jp.katakana_ri",  # リ
            "jp.katakana_ru",  # ル
            "jp.katakana_re",  # レ
            "jp.katakana_ro",  # ロ
            "jp.katakana_wa",  # ワ
            "jp.katakana_wo",  # ヲ
        ],
        [
            "jp.katakana_n",  # ン
            # jp numerals (these are spaced/sized to match the rest of the jp font)
            "jp.zero",
            "jp.one",
            "jp.two",
            "jp.three",
            "jp.four",
            "jp.five",
            "jp.six",
            "jp.seven",
            "jp.eight",
            "jp.nine",
            # jp uppercase latin characters (these are spaced/sized to match the rest of the jp font)
            "jp.upper_a",
            "jp.upper_b",
            "jp.upper_c",
            "jp.upper_d",
            "jp.upper_e",
        ],
        [
            "jp.upper_f",
            "jp.upper_g",
            "jp.upper_h",
            "jp.upper_i",
            "jp.upper_j",
            "jp.upper_k",
            "jp.upper_l",
            "jp.upper_m",
            "jp.upper_n",
            "jp.upper_o",
            "jp.upper_p",
            "jp.upper_q",
            "jp.upper_r",
            "jp.upper_s",
            "jp.upper_t",
            "jp.upper_u",
        ],
        [
            "jp.upper_v",
            "jp.upper_w",
            "jp.upper_x",
            "jp.upper_y",
            "jp.upper_z",
            # jp lowercase latin characters (these are spaced/sized to match the rest of the jp font)
            "jp.lower_a",
            "jp.lower_b",
            "jp.lower_c",
            "jp.lower_d",
            "jp.lower_e",
            "jp.lower_f",
            "jp.lower_g",
            "jp.lower_h",
            "jp.lower_i",
            "jp.lower_j",
            "jp.lower_k",
        ],
        [
            "jp.lower_l",
            "jp.lower_m",
            "jp.lower_n",
            "jp.lower_o",
            "jp.lower_p",
            "jp.lower_q",
            "jp.lower_r",
            "jp.lower_s",
            "jp.lower_t",
            "jp.lower_u",
            "jp.lower_v",
            "jp.lower_w",
            "jp.lower_x",
            "jp.lower_y",
            "jp.lower_z",
            None,  # no character data here
        ],
        [
            # jp punctuation (these are spaced/sized to match the rest of the jp font)
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
            # jp miscellaneous
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
            "en.coin",
            "en.circle",
            "en.square",
            "en.triangle",
            "en.rhombus",  # diagonal square
            # other symbols
            "en.address",  # at symbol @
        ],
        [
            "en.music",  # musical note
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
            # two character abbreviation for pokemon
            "en.pkmn_pk",
        ],
        [
            "en.pkmn_mn",
            # more whitespace
            "",
            "",
            "",
            "",
            "",
            "",
            # new characters added in platinum
            "",  # degree symbol?
            "",  # underscore?
            "",  # wide underscore?
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
        ).union(set([8 + 30 * 16, 9 + 30 * 16]))
        else None
    )
    for i in range(32 * 16)
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
                print(f"Duplicate character filename found in normal_fontmap at {i}: {data_0[i]}")

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
                print(f"Duplicate character filename found in bold_fontmap at {i}: {data_2[i]}")

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
