reset = "\033[0m"
bold = "\033[1m"
italic = "\033[3m"


class FilenameNotFoundError(Exception):
    """An exception class for when "" is found but not expected in the filename list"""


class CharacterDataNotFoundError(Exception):
    """An exception class for when None is found but not expected in the filename list"""
