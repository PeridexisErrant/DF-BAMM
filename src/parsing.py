'''
Created on May 21, 2015

@author: Button
'''

import re

from . import config


# Values used to escape problematic literal characters
ascii_codes = {c: ord(c) for c in "&'*,:?[]|"}

userlog = config.userlog
modderslog = config.modderslog


def tags(line):
    """Return an ordered list of all the tags in this line, without brackets,
    with literals escaped if necessary."""
    processed_line = escape_problematic_literals(line)
    to_return = []        # list of strings, a la split()
    while ('[' in processed_line and
           ']' in processed_line and
           processed_line.index('[') < processed_line.rindex(']')):

        if processed_line.index(']') < processed_line.index('['):
            processed_line = processed_line[processed_line.index('['):]

        to_return.append(processed_line[processed_line.index('[')+1:
                                        processed_line.index(']')])

        processed_line = processed_line[processed_line.index(']')+1:]
    return to_return


def escape_problematic_literals(line):
    """ Returns line with its char literals replaced with their cp437 codes.

    Char literals are usually used for defining tiles, and are two single
    quotes around a character, so: '*'. Since this is the only case in which
    the DF raw characters ']', '[' and ':' are allowed within a tag outside
    their uses, and since cp437 codes are equally valid, replacing these with
    their cp437 codes is harmless and streamlines lexing considerably.
    """
    # Replace literal key characters with number codes
    # Literal colons are going to require some special processing, because of
    # the following case:  GROWTH:'r':'x': etc. That's why we can't just use
    # a blind replaceAll.

    # If odd, we are inside a tag. If even, we are outside a tag.
    bracketscount = 0
    count = 0                # Where we are in the string
    quotescount = 0
    while count < len(line)-2:
        # Going from inside a tag to outside or vice versa
        if (((bracketscount % 2 == 0 and line[count] == "[") or
             (bracketscount % 2 == 1 and line[count] == "]"))):
            bracketscount += 1
        # We are inside a tag and we have discovered a ' character beginning a
        # literal value, with another 2 characters down on the other side.
        elif (quotescount % 2 == 0 and bracketscount % 2 == 1 and
              line[count:count+3] in ascii_codes.keys()):
            # If the character could be a problem for later processing, replace
            #  it with its ascii code.
            line = line[:count] + ascii_codes[line[count:count+3]] + \
                line[count+3:]
        elif line[count] == "'":
            quotescount += 1
        elif bracketscount % 2 == 1 and line[count] == ':':
            quotescount = 0
        count += 1
    # line has now had its literal "use this tile" versions of its special
    # characters replaced with their numbers.
    return line


def path_compatible(full_path, allowed_paths):
    """Return True if full_path regex matches anything in allowed_paths, or
    False otherwise."""
    full_path = full_path.replace('\\', '/')
    for allowed_path in allowed_paths:
        allowed_path = allowed_path.replace('\\', '/')
        match = re.match(allowed_path, full_path)
        if match is not None:
            return True
    return False
