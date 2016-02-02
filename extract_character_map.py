#!/usr/bin/python3

# https://rosettacode.org/wiki/Basic_bitmap_storage/Python
from collections import namedtuple
from copy import copy

Colour = namedtuple('Colour','r,g,b')
Colour.copy = lambda self: copy(self)

black = Colour(0,0,0)
white = Colour(255,255,255) # Colour ranges are not enforced.

class Bitmap():
    def __init__(self, width = 40, height = 40, background=white):
        assert width > 0 and height > 0 and type(background) == Colour
        self.width = width
        self.height = height
        self.background = background
        self.map = [[background.copy() for w in range(width)] for h in range(height)]

    def fillrect(self, x, y, width, height, colour=black):
        assert x >= 0 and y >= 0 and width > 0 and height > 0 and type(colour) == Colour
        for h in range(height):
            for w in range(width):
                self.map[y+h][x+w] = colour.copy()

    def chardisplay(self):
        txt = [''.join(' ' if bit==self.background else '@'
                       for bit in row)
               for row in self.map]
        # Boxing
        txt = ['|'+row+'|' for row in txt]
        txt.insert(0, '+' + '-' * self.width + '+')
        txt.append('+' + '-' * self.width + '+')
        print('\n'.join(txt))

    def set(self, x, y, colour=black):
        assert type(colour) == Colour
        self.map[y][x]=colour

    def get(self, x, y):
         return self.map[y][x]

    def view(self, x, y, width, height):
         view = Bitmap(width, height, background=self.background)
         for vx in range(0, width):
             for vy in range(0, height):
                 view.set(vx, vy, self.get(x + vx, y + vy))
         return view

# https://rosettacode.org/wiki/Bitmap/Read_a_PPM_file

def tokenize(f):
    for line in f:
        line = line.decode('us-ascii')
        if line[0] != '#':
            for t in line.split():
                yield t

def ppmp6tobitmap(f):
    t = tokenize(f)
    nexttoken = lambda : next(t)
    assert 'P6' == nexttoken(), 'Wrong filetype'
    width, height, maxval = (int(nexttoken()) for i in range(3))
    assert maxval == 255
    bitmap = Bitmap(width, height, Colour(0, 0, 0))
    for h in range(0, height):
        for w in range(0, width):
            bitmap.set(w, h, Colour(*(f.read(3))))
    return bitmap

def print_character(character):
    assert len(character) == 8
    for row in character:
        assert len(row) == 5
        print(''.join('@' if col else ' ' for col in row))

with open('character-map.ppm', 'rb') as f:
    bitmap = ppmp6tobitmap(f)

TABLE_START_X = 54
TABLE_START_Y = 41
CHARACTER_WIDTH = 23
CHARACTER_HORIZONTAL_SPACING = 1
CHARACTER_HEIGHT = 32
CHARACTER_VERTICAL_SPACING = 1
PIXEL_TABLE_START_X = 4
PIXEL_TABLE_START_Y = 5
PIXEL_WIDTH = 2
PIXEL_HEIGHT = 2
PIXEL_HORIZONTAL_SPACING = 1
PIXEL_VERTICAL_SPACING = 1

characters = []

x = TABLE_START_X
for character_col in range(0, 0b10000):
    y = TABLE_START_Y
    for character_row in range(0, 0b10000):
        view = bitmap.view(x, y, CHARACTER_WIDTH, CHARACTER_HEIGHT)
        characters.append(
            [ [ view.get(PIXEL_TABLE_START_X + pixel_col * (PIXEL_WIDTH + PIXEL_HORIZONTAL_SPACING),
                         PIXEL_TABLE_START_Y + pixel_row * (PIXEL_HEIGHT + PIXEL_VERTICAL_SPACING)) == black
                for pixel_col in range(0, 5) ]
              for pixel_row in range(0, 8)
            ])
        y += CHARACTER_HEIGHT + CHARACTER_VERTICAL_SPACING
    x += CHARACTER_WIDTH + CHARACTER_HORIZONTAL_SPACING

print('CHARACTER_MAP = [')
for index, character in enumerate(characters):
    print("    # 0b{:08b}:".format(index))
    assert len(character) == 8
    print("    [")
    for row in character:
        assert len(row) == 5
        print("        ", row, end=',\n')
    print("    ],")
print(']')
