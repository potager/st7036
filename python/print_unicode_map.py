#!/usr/bin/python3

characters = []

with open('../UNICODE_MAP') as f:
    for line in f:
        charcode, codepoint, chardesc = line.strip().split("\t")
        if codepoint.startswith('U+'):
            characters.append(chr(int(codepoint[2:], base=16)))
        else:
            characters.append(' ')

for row_index in range(0, 16):
    for column_index in range(0, 16):
        print(characters[row_index + column_index * 16], end='')
    print()
