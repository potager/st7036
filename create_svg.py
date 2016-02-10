#!/usr/bin/python3

import sys

STYLE = """
    rect {
      stroke:none;
    }
    #background {
      fill: url(#backlight);
    }
    .character-background {
      fill: #ccc;
      fill-opacity: 0.1;
    }
    .pixel {
      fill: #000000;
      fill-opacity: 0;
    }
    .pixel-on {
      fill-opacity: 1;
    }
    .pixel-off {
      fill-opacity: 0.0;
    }
    .button {
      fill-opacity: 0.3;
    }
"""

SCRIPT = """
    var sheet = document.styleSheets[0];
    var displayOffRuleIndex;
    var contrastRuleIndices;
    var backlightLedRuleIndices = [0, 0, 0, 0, 0, 0];

    function setPixel(x_hex, y_hex, on) {
      var pixel_id = 'pixel-' + x_hex + '-' + y_hex;
      var pixel = document.getElementById(pixel_id);
      // There's sometimes a race before everything is set up, so
      // let's not crash in that case
      if (pixel && pixel.classList) {
        pixel.classList.toggle('pixel-on', on);
        pixel.classList.toggle('pixel-off', !on);
      }
    }
    function turnDisplayOn() {
      if (displayOffRuleIndex) {
        sheet.deleteRule(displayOffRuleIndex);
      }
    }
    function turnDisplayOff() {
      if (!displayOffRuleIndex) {
        displayOffRuleIndex = sheet.cssRules.length;
        sheet.insertRule('.pixel { visible: false }', displayOffRuleIndex);
      }
    }
    function setContrast(opacity) {
      if (!contrastRuleIndices) {
        contrastRuleIndices = [sheet.cssRules.length, sheet.cssRules.length + 1];
      } else {
        sheet.deleteRule(contrastRuleIndices[1]);
        sheet.deleteRule(contrastRuleIndices[0]);
      }
      on_opacity = 2 - (2 * opacity)
      off_opacity = 1 - (2 * opacity)
      sheet.insertRule('.pixel-on  { fill-opacity: ' + ((on_opacity > 1) ? 1 : on_opacity) + '; }', contrastRuleIndices[0]);
      sheet.insertRule('.pixel-off { fill-opacity: ' + ((off_opacity < 0) ? 0 : off_opacity) +  '; }', contrastRuleIndices[1]);
    }
    function setBacklightColor(ledIndex, red, green, blue) {
      var color = 'rgb(' + red + ',' + green + ',' + blue + ')';
      if (!backlightLedRuleIndices[ledIndex]) {
        backlightLedRuleIndices[ledIndex] = sheet.cssRules.length;
      } else {
        sheet.deleteRule(backlightLedRuleIndices[ledIndex]);
      }
      sheet.insertRule('.backlight-led' + ledIndex + ' { stop-color: ' + color + '; }', backlightLedRuleIndices[ledIndex]);
    } 

    function forwardMouseDown(button) {
      window.location = 'event://mouse-down/' + button;
    }
    function forwardMouseUp(button) {
      window.location = 'event://mouse-up/' + button;
    }
    
"""

SVG_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   xmlns="http://www.w3.org/2000/svg"
   width="628"
   height="547"
   id="lcd"
   version="1.1">
   >
  <style title="default" type="text/css">
    <![CDATA[{style}]]>
  </style>
  <style title="display-on-off" type="text/css"></style>
  <style title="contrast" type="text/css"></style>
  <script type="text/javascript">
    <![CDATA[{script}]]>
  </script>
  <defs>
    <linearGradient id="backlight">
      <stop class="backlight-led0" offset="0%" style="stop-opacity: 0.8" /> 
      <stop class="backlight-led0" offset="5%" /> 
      <stop class="backlight-led1" offset="23%" /> 
      <stop class="backlight-led2" offset="41%" /> 
      <stop class="backlight-led3" offset="59%" /> 
      <stop class="backlight-led4" offset="77%" /> 
      <stop class="backlight-led5" offset="95%" /> 
      <stop class="backlight-led5" offset="100%" style="stop-opacity: 0.8" /> 
    </linearGradient>
  </defs>
  <image x="0" y="0" width="628" height="546" xlink:href="background.jpg" />
  <rect id="button-cancel" class="button" x="4"   y="88"  width="36"  height="100" onmousedown="forwardMouseDown('cancel')" onmouseup="forwardMouseUp('cancel')"/>
  <rect id="button-up"     class="button" x="4"   y="220" width="36"  height="100" onmousedown="forwardMouseDown('up')"     onmouseup="forwardMouseUp('up')"    />
  <rect id="button-down"   class="button" x="4"   y="330" width="36"  height="100" onmousedown="forwardMouseDown('down')"   onmouseup="forwardMouseUp('down')"  />
  <rect id="button-left"   class="button" x="114" y="488" width="112" height="56"  onmousedown="forwardMouseDown('left')"   onmouseup="forwardMouseUp('left')"  />
  <rect id="button-enter"  class="button" x="258" y="488" width="112" height="56"  onmousedown="forwardMouseDown('enter')"  onmouseup="forwardMouseUp('enter')" />
  <rect id="button-right"  class="button" x="404" y="488" width="112" height="56"  onmousedown="forwardMouseDown('right')"  onmouseup="forwardMouseUp('right')" />
  <rect
     style="fill-opacity: 1;"
     id="background"
     width="528"
     height="171"
     x="48"
     y="234"/>
  <g transform="translate(64, 249) scale({scale})">
  <g id="display" transform="translate(1.41,1.245)">
    <rect
       style="fill-opacity: 0;"
       id="plane"
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
      <rect x="0" y="0" width="{width:f}" height="{height:f}" class="character-background" />
      {pixels}
    </g>
"""

PIXEL_TEMPLATE = """
      <rect id="pixel-0x{column:02x}-0x{row:02x}"
            x="{x:f}" y="{y:f}" width="{width:f}" height="{height:f}"
            class="pixel" />
"""

SCALE = 9.8
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
pos_pixel_y = 0
for character_row in range(0, CHARACTER_ROWS):
    character_x = 0
    pos_pixel_x = 0
    for character_column in range(0, CHARACTER_COLUMNS):
        ddram_address = character_row * 0x10 + character_column
        pixels = []
        pixel_y = 0
        for pixel_row in range(0, PIXEL_ROWS):
            pixel_x = 0
            for pixel_column in range(0, PIXEL_COLUMNS):
                pixels.append(PIXEL_TEMPLATE.format(row=pos_pixel_y, column=pos_pixel_x, x=pixel_x, y=pixel_y, width=PIXEL_WIDTH, height=PIXEL_HEIGHT))
                pixel_x += PIXEL_WIDTH + PIXEL_HORIZONTAL_SPACING
                pos_pixel_x += 1
            pixel_y += PIXEL_HEIGHT + PIXEL_VERTICAL_SPACING
            pos_pixel_x -= PIXEL_COLUMNS
            pos_pixel_y += 1
        characters.append(CHARACTER_TEMPLATE.format(address=ddram_address, x=character_x, y=character_y, width=CHARACTER_WIDTH, height=CHARACTER_HEIGHT, pixels=''.join(pixels)))
        character_x += CHARACTER_WIDTH + CHARACTER_HORIZONTAL_SPACING
        pos_pixel_x += PIXEL_COLUMNS
        pos_pixel_y -= PIXEL_ROWS
    character_y += CHARACTER_HEIGHT + CHARACTER_VERTICAL_SPACING
    pos_pixel_y += PIXEL_ROWS
print(SVG_TEMPLATE.format(style=STYLE, script=SCRIPT, scale=SCALE, characters=''.join(characters)))
