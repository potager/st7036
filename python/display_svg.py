from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import WebKit

import itertools
import random
import time
from threading import Thread

from character_map import CHARACTER_MAP
import st7036_codec

VALID_DDRAM_ADDRESSES = list(range(0x00, 0x30))
USER_DEFINED_CHARS = 8

def print_character(character):
    assert len(character) == 8
    for row in character:
        assert len(row) == 5
        print(''.join('@' if col else ' ' for col in row))

BLANK_CHARACTER = [[False] * 5] * 8

class st7036():
    def __init__(self):
        self._cgram = ([BLANK_CHARACTER] * USER_DEFINED_CHARS) + CHARACTER_MAP[USER_DEFINED_CHARS:]
        self._ddram = [0] * 80
        self._cursor_offset = 0
        self.rows = 3
        self.columns = 16
        self.row_offsets = [0x00, 0x10, 0x20]
        self._enabled = True
        self._cursor_enabled = False
        self._cursor_blink = False
        # XXX self._double_height
        self.animations = [] * USER_DEFINED_CHARS
        self.update_display_mode()
        # XXX set entry mode (no shift, cursor direction)
        self.set_bias(1)
        self.set_contrast(40)
        self.clear()

    def read_ddram(self, offset):
        return self._ddram[offset]

    def read_cgram(self, offset):
        return self._cgram[offset]

    def set_bias(self, bias=1):
        # XXX
        pass

    def set_contrast(self, contrast):
        if type(contrast) is not int:
            raise TypeError("contrast must be an integer")

        if contrast not in range(0, 0x40):
            raise ValueError("contrast must be an integer in the range 0..0x3F")

        # XXX
        pass

    def set_display_mode(self, enabled=True, cursor=False, blink=False):
        self._enabled = enable
        self._cursor_enabled = cursor
        self._cursor_blink = blink
        self.update_display_mode()

    def update_display_mode(self):
        # enable display, cursor, blink
        pass

    def enable_cursor(self, cursor=False):
        self._cursor_enabled = cursor
        self.update_display_mode()

    def enable_blink(self, blink=False):
        self._cursor_blink = blink
        self.update_display_mode()

    def set_cursor_offset(self, offset):
        assert offset in VALID_DDRAM_ADDRESSES
        self._cursor_offset = offset

    def set_cursor_position(self, column, row):
        if row not in range(self.rows) or column not in range(self.columns):
            raise ValueError("row and column must integers within the defined screen size")

        offset = self.row_offsets[row] + column
        self.set_cursor_offset(offset)

    def home(self):
        self.set_cursor_position(0, 0)

    def clear(self):
        for i in range(0, len(self._ddram)):
            self._ddram[i] = 0
        self.home()

    def write(self, value):
        for index, byte in enumerate(value.encode('st7036', errors='replace')):
            self._ddram[self._cursor_offset + index] = byte

    def create_animation(self, anim_pos, anim_map, frame_rate):
        self.create_char(anim_pos, anim_map[0])
        self.animations[anim_pos] = [anim_map, frame_rate]
        self.set_cursor_position(0, 1)

    def update_animations(self):
        for i, animation in enumerate(self.animations):
            if len(animation) == 2:
                anim = animation[0]
                fps = animation[1]
                frame = anim[int(round(time.time()*fps) % len(anim))]
                self.create_char(i, frame)
        self.set_cursor_position(0, 1)

    def create_char(self, char_pos, char_map):
        if char_pos not in range(0, USER_DEFINED_CHARS):
            return False
        self._cgram[char_pos] = [ [ '1' == c for c in "{:05b}".format(line) ] for line in char_map ]

    def cursor_left(self):
        if self._cursor_offset > 0:
            self._cursor_offset -= 1

    def cursor_right(self):
        if self._cursor_offset < 0x30:
            self._cursor_offset += 1

    def shift_left(self):
        # XXX
        pass

    def shift_right(self):
        # XXX
        pass

    def double_height(self, enable=0, position=1):
        # XXX
        pass

class Example(Gtk.Window):
    def __init__(self, st7036):
        super(Example, self).__init__()
        self.exiting = False
        self.st7036 = st7036
        self.init_ui()

    def init_ui(self):
        vbox = Gtk.VBox()

        self.display = WebKit.WebView()
        #self.display.load_html_string('<img src="file:///home/lunar/Documents/Misc/TouPi/st7036/lcd.svg" width="612" height="164" />', 'file:///')
        self.display.load_uri('file:///home/lunar/Documents/Misc/TouPi/st7036/lcd.svg')
        vbox.pack_start(self.display, expand=True, fill=True, padding=0)

        b = Gtk.Button("Run")
        b.connect("clicked", self.on_click_run)
        vbox.pack_start(b, expand=False, fill=False, padding=0)

        self.add(vbox)

        self.set_title("GTK window")
        self.resize(420, 120)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", self.handle_quit)
        self.show_all()

    def handle_quit(self, *args):
        self.exiting = True
        if hasattr(self, 'update_thread'):
            self.update_thread.join()
        Gtk.main_quit()

    def on_click_run(self, button):
        GLib.timeout_add(200, self.update_display)
        self.update_thread = Thread(target=do_stuff)
        self.update_thread.start()

    def set_pixel_state(self, ddram_address, row, column, on=True):
        if ddram_address not in VALID_DDRAM_ADDRESSES:
            raise ValueError('DDRAM address outside display')
        if on:
            opacity = 1
        else:
            opacity = 0
        self.display.execute_script("document.getElementById('ddram-0x{ddram_address:02x}-pixel-0x{row:02x}-b{column:x}').style.fillOpacity = {opacity};".format(ddram_address=ddram_address, row=row, column=column, opacity=opacity))

    def display_char(self, ddram_address, charcode):
        char = self.st7036.read_cgram(charcode)
        for row, line in enumerate(char):
            for column, pixel_state in enumerate(reversed(line)):
                self.set_pixel_state(ddram_address, row, column, on=pixel_state)

    def update_display(self):
        for offset in range(0, 0x30): # XXX
            self.display_char(offset, self.st7036.read_ddram(offset))
        return not self.exiting

# http://www.spooky-possum.org/wordpress/?p=52

def run_delayed_generator(generator):
    """Run this function with a generator as it's argument. Whenever
       that function performs a "yield n" then the function will be
       delayed by n seconds. i.e. "yield n" acts like "sleep (n)"
       without blocking the GTK main loop."""
    try:
        t = next(generator)
        GLib.timeout_add(int(t*1000), run_delayed_generator, generator)
    except StopIteration:
        pass
    return False

def run_delayed(fn):
    def wrapper(*args):
        run_delayed_generator(fn(*args))
    return wrapper

pirate = [
    [0x00, 0x1f, 0x0b, 0x03, 0x00, 0x04, 0x11, 0x1f],
    [0x00, 0x1f, 0x16, 0x06, 0x00, 0x08, 0x03, 0x1e],
    [0x00, 0x1f, 0x0b, 0x03, 0x00, 0x04, 0x11, 0x1f],
    [0x00, 0x1f, 0x05, 0x01, 0x00, 0x02, 0x08, 0x07]
]

heart = [
    [0x00, 0x0a, 0x1f, 0x1f, 0x1f, 0x0e, 0x04, 0x00],
    [0x00, 0x00, 0x0a, 0x0e, 0x0e, 0x04, 0x00, 0x00],
    [0x00, 0x00, 0x00, 0x0e, 0x04, 0x00, 0x00, 0x00],
    [0x00, 0x00, 0x0a, 0x0e, 0x0e, 0x04, 0x00, 0x00]
]

pacman = [
    [0x0e, 0x1f, 0x1d, 0x1f, 0x18, 0x1f, 0x1f, 0x0e],
    [0x0e, 0x1d, 0x1e, 0x1c, 0x18, 0x1c, 0x1e, 0x0f]
]

colours = [
    "\x01   much red   \x01",
    "\x01  very orange \x01",
    "\x01  many yellow \x01",
    "\x01   also green \x01",
    "\x01   such blue  \x01",
    "\x01  so indigo   \x01",
    "\x01  ahoy voilet \x01"]

def get_anim_frame(char, fps):
    return char[int(round(time.time() * fps) % len(char))]



lcd = st7036()

@run_delayed
def do_stuff():
#    print(">> fill screen")
#    for i in range(48):
#        lcd.set_cursor_offset(i)
#        yield .02
#        lcd.write(chr(i+65))
#        yield .02
#    lcd.clear()
#    print(">> cycle character set")
#    for i in range(256 - 48 - 65):
#        lcd.set_cursor_offset(0x00)
#        lcd.write(bytes([(i + j + 65) for j in range(48)]).decode('st7036'))
#        print("wrote, yielding")
#        yield .06
#        lcd.clear()
    lcd.set_cursor_position(0, 0)
    lcd.write('Coucou Alys')
    lcd.set_cursor_position(3, 1)
    lcd.write(' et Aurélie !')
    yield 0.2

#    lcd.set_cursor_position(0, 0)
#    lcd.write(chr(0) + " such rainbow!")
#
#    x = 0
#
#    text = "  pimoroni ftw  "
#
#    while True:
#        x += 3
#        x %= 360
#
#        #backlight.sweep((360.0 - x) / 360.0)
#        #backlight.set_graph(abs(math.sin(x / 100.0)))
#
#        if x == 0:
#            lcd.set_cursor_position(0, 1)
#            lcd.write(" " * 16)
#
#        pos = int(x / 20)
#        lcd.set_cursor_position(0, 1)
#        lcd.write(text[:pos] + "\x02")
#
#        lcd.set_cursor_position(0, 2)
#        lcd.write(colours[int(x / 52)])
#
#        lcd.create_char(0, get_anim_frame(pirate, 2))
#        lcd.create_char(1, get_anim_frame(heart, 2))
#        lcd.create_char(2, get_anim_frame(pacman, 2))
#
#        yield 0.05

def main():
    app = Example(lcd)
    Gtk.main()

if __name__ == "__main__":
    main()
