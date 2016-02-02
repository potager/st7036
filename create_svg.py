#!/usr/bin/python3

import sys

STYLE = """
    rect {
      fill-opacity: 1;
      stroke:none;
    }
    #background {
      fill: #d9d9d9;
    }
    .pixel-background {
      fill: #d9518f;
    }
    .pixel {
      fill: #000000;
      fill-opacity: 0;
    }
"""

SVG_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   width="{width:f}"
   height="{height:f}"
   id="lcd"
   version="1.1">
   >
  <style type="text/css">
    {style}
  </style>
  <g transform="scale({scale})">
  <g id="display" transform="translate(1.41,1.245)">
    <rect
       style=""
       id="background"
       width="48.18"
       height="12.01"
       x="0"
       y="0"/>
    <g id="slant" transform="translate(0.24, 0) matrix(1 0 -0.019 1 0 0)">
    {characters}
    </g>
  </g>
  </g>
</svg>
"""

CHARACTER_TEMPLATE = """
    <g id="ddram-0x{address:02x}" transform="translate({x:f},{y:f})">
      <rect x="0" y="0" width="{width:f}" height="{height:f}" class="pixel-background" />
      {pixels}
    </g>
"""

PIXEL_TEMPLATE = """
      <rect id="ddram-0x{ddram_address:02x}-pixel-0x{row:02x}-b{column:x}"
            x="{x:f}" y="{y:f}" width="{width:f}" height="{height:f}" 
            class="pixel" />
"""

SCALE = 12
DISPLAY_WIDTH = 51
DISPLAY_HEIGHT = 14.5
CHARACTER_ROWS = 3
CHARACTER_COLUMNS = 16
CHARACTER_WIDTH = 2.47
CHARACTER_HEIGHT = 3.65
CHARACTER_HORIZONTAL_SPACING = 3.03 - 2.47
CHARACTER_VERTICAL_SPACING = 4.18 - 3.65
PIXEL_ROWS = 8
PIXEL_COLUMNS = 5
PIXEL_WIDTH = 0.47
PIXEL_HEIGHT = 0.43
PIXEL_HORIZONTAL_SPACING = 0.03
PIXEL_VERTICAL_SPACING = 0.03
    

characters = []
character_y = 0
for character_row in reversed(range(0, CHARACTER_ROWS)):
    character_x = 0
    for character_column in range(0, CHARACTER_COLUMNS):
        ddram_address = character_row * 0x10 + character_column
        pixels = []
        pixel_y = 0
        for pixel_row in reversed(range(0, PIXEL_ROWS)):
            pixel_x = 0
            for pixel_column in reversed(range(0, PIXEL_COLUMNS)):
                pixels.append(PIXEL_TEMPLATE.format(ddram_address=ddram_address, row=pixel_row, column=pixel_column, x=pixel_x, y=pixel_y, width=PIXEL_WIDTH, height=PIXEL_HEIGHT))
                pixel_x += PIXEL_WIDTH + PIXEL_HORIZONTAL_SPACING
            pixel_y += PIXEL_HEIGHT + PIXEL_VERTICAL_SPACING
        characters.append(CHARACTER_TEMPLATE.format(address=ddram_address, x=character_x, y=character_y, width=CHARACTER_WIDTH, height=CHARACTER_HEIGHT, pixels=''.join(pixels)))
        character_x += CHARACTER_WIDTH + CHARACTER_HORIZONTAL_SPACING
    character_y += CHARACTER_HEIGHT + CHARACTER_VERTICAL_SPACING
print(SVG_TEMPLATE.format(style=STYLE, scale=SCALE, width=SCALE * DISPLAY_WIDTH, height=SCALE * DISPLAY_HEIGHT, characters=''.join(characters)))
