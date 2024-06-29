from collections.abc import Iterable
from bidict import bidict, ValueDuplicationError
import font.readfont_index


# minimal sets of chars that can be useful in general
lower_alpha = set("abcdefghijklmnopqrstuvwxyz")
upper_alpha = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
alphabet = lower_alpha | upper_alpha
numbers = set("0123456789")
# do we ever need to identify punctuation?
# punctuation = set("$!?,.•/‘’“”„«»()♂♀+-*#=&~:;")
# ellipsis … may not be used in english version of game

# charsets for each part of the logic
locations = alphabet | set("-")  # double-check this
# species = alphabet | set("-2")  # this is definitely missing stuff

# # sets of char img data corresponding to charsets above
# data_locations = image of locations under normal_fontmap
# data_species = image of species under normal_fontmap
# # potentially something that uses bold_fontmap (like level, gender)
# # etc ...

# probably some kind of class or something that details the english tracker logic

## Locations research
# https://bulbapedia.bulbagarden.net/wiki/List_of_locations_by_index_number_(Generation_IV)
# Obviously uppercase and lowercase alphabet, accent e (we can pretend there's no accent), period, apostrophe (?),


def image(x: Iterable, f: function):
    """utility function for taking the image of a set under a function/mapping"""
    return set(f(y) for y in x)
