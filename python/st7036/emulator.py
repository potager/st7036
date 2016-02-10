import sys
import threading
import time
import itertools

from character_map import CHARACTER_MAP

class spidev_adapter(object):
    """Mimics spidev module"""

    def __init__(self, controller):
        self._controller = controller

    def SpiDev(self):
        return SpiDev(self._controller)


class SpiDev(object):
    def __init__(self, controller):
        self._controller = controller

    def open(self, bus, chip_select):
        pass

    @property
    def max_speed_hz(self):
        pass

    @max_speed_hz.setter
    def max_speed_hz(self, value):
        pass

    def xfer(self, input_bytes):
        return self._controller.spi_xfer(input_bytes)


class GPIO_adapter(object):
    """Mimics RPi.GPIO module"""

    BCM = 0
    OUT = 0
    LOW = 0
    HIGH = 1

    def __init__(self, controller):
        self._controller = controller

    def setmode(self, mode):
        pass

    def setwarnings(self, on):
        pass

    def setup(self, pin, direction):
        pass

    def output(self, pin, value):
        self._controller.gpio_output(pin, value)


class Display(object):
    @property
    def lines(self):
        pass # 1, 2 or 3

    @property
    def columns(self):
        pass # maximum: 20 for 1-2 lines, 16 for 3 lines

    def set_pixel(self, x, y, on=True):
        ...

    def turn_display_on(self):
        ...

    def turn_display_off(self):
        ...

    def change_contrast(self, value):
        ...

import atexit
from blessings import Terminal

class ThreeLinesCursesDisplay(Display):
    def __init__(self):
        self._term = Terminal()
        self._pixels = [[False] * (self.columns * ST7036.CHARACTER_WIDTH) for y in range(self.lines * ST7036.CHARACTER_HEIGHT)]
        self._enabled = False
        self._location_map = self._get_location_map()
        atexit.register(lambda: print(self._term.exit_fullscreen))
        print(self._term.enter_fullscreen)
        print(self._term.clear)

    @property
    def lines(self):
        return 3

    @property
    def columns(self):
        return 16

    def _get_location_map(self):
        location_map = []
        term_y = self._term.height - 1
        for line_index in range(self.lines):
            for vertical_pixel in range(ST7036.CHARACTER_HEIGHT):
                line_map = []
                term_x = 0
                for column_index in range(self.columns):
                    for horiz_pixel in range(ST7036.CHARACTER_WIDTH):
                        line_map.append((term_x, term_y))
                        term_x += 1
                    term_x += 1
                location_map.append(line_map)
                term_y -= 1
            term_y -= 1
        return list(reversed(location_map))

    def _draw_pixel(self, x, y):
        term_x, term_y = self._location_map[y][x]
        with self._term.location(term_x, term_y):
            if self._pixels[y][x]: print('@', end='')
            else:                  print(' ', end='')
        sys.stdout.flush()

    def _redraw(self):
        if not self._enabled:
            return
        for y in range(self.lines * ST7036.CHARACTER_HEIGHT):
            for x in range(self.columns * ST7036.CHARACTER_WIDTH):
                self._draw_pixel(x, y)

    def set_pixel(self, x, y, on=True):
        self._pixels[y][x] = on
        if not self._enabled:
            return
        self._draw_pixel(x, y)

    def switch_display(self, on=True):
        self._enabled = on
        self._redraw()

    def turn_display_on(self):
        self.switch_display(on=True)

    def turn_display_off(self):
        self.switch_display(on=False)


from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import WebKit


def glib_defer(f):
    def wrapper(*args, **kwargs):
        GLib.idle_add(f, *args, **kwargs)
    return wrapper


class GTKDisplay(Display, Gtk.Window):
    def __init__(self):
        super().__init__()
        self._display_on = True
        self._scripts = []
        self._scripts_lock = threading.Lock()
        self._scripts_condition = threading.Condition()
        self.init_ui()
        threading.Thread(target=self.run_main_loop).start()
        t = threading.Thread(target=self.run_scripts_loop)
        t.daemon = True
        t.start()

    def run_main_loop(self):
        Gtk.main()

    @glib_defer
    def init_ui(self):
        vbox = Gtk.VBox()

        self.display = WebKit.WebView()
        #self.display.load_html_string('<img src="file:///home/lunar/Documents/Misc/TouPi/st7036/lcd.svg" width="612" height="164" />', 'file:///')
        self.display.load_uri('file:///home/lunar/Documents/Misc/TouPi/st7036/lcd.svg')
        self.display.connect('navigation-requested', self._on_navigation_requested)
        vbox.pack_start(self.display, expand=True, fill=True, padding=0)

        self.add(vbox)

        self.set_title("ST7036 emulator")
        self.resize(420, 120)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", self.handle_quit)
        self.show_all()

    def handle_quit(self, *args):
        Gtk.main_quit()

    @property
    def lines(self):
        return 3

    @property
    def columns(self):
        return 16

    def run_scripts_loop(self):
        with self._scripts_condition:
            while True:
                self._scripts_lock.acquire()
                if not self._scripts:
                    self._scripts_lock.release()
                    self._scripts_condition.wait()
                    time.sleep(.001)
                    self._scripts_lock.acquire()
                self.run_script('\n'.join(self._scripts))
                self._scripts.clear()
                self._scripts_lock.release()

    def execute_script(self, script):
        with self._scripts_condition:
            with self._scripts_lock:
                self._scripts.append(script)
            self._scripts_condition.notify()

    @glib_defer
    def run_script(self, script):
        self.display.execute_script(script)

    def set_pixel(self, x, y, on=True):
        if on:
            value = 'true'
        else:
            value = 'false'
        self.execute_script("setPixel('0x{x:02x}', '0x{y:02x}', {value});".format(x=x, y=y, value=value))

    def turn_display_on(self):
        if self._display_on:
            return
        self.execute_script("turnDisplayOn();")
        self._display_enabled = True

    def turn_display_off(self):
        if not self._display_on:
            return
        self.execute_script("turnDisplayOff();")
        self._display_enabled = False

    def change_contrast(self, value):
        opacity = value / 0x40
        self.execute_script("setContrast({opacity});".format(opacity=opacity))

    def set_backlight_color(self, led_index, red, green, blue):
        self.execute_script("setBacklightColor({led_index}, {red:d}, {green}, {blue});".format(led_index=led_index, red=int(red), green=int(green), blue=int(blue)))

    def _on_navigation_requested(self, view, frame, req, data=None):
        uri = req.get_uri()
        print('nav req', uri)
        if not uri.startswith('event://'):
            return False
        parts = uri.split('/')[2:]
        event, args = parts[0], parts[1:]
        getattr(self, '_handle_{}'.format(event.replace('-', '_')))(*args)
        return True

    def _handle_mouse_down(self, button):
        print('button down', button)

    def _handle_mouse_up(self, button):
        print('button up', button)

class Controller(object):
    GPIO_LOW = 0
    GPIO_HIGH = 1

    RESET_PIN = 1
    REGISTER_SELECT_PIN = 25
    READ_WRITE_PIN = 3

    def __init__(self, st7036):
        self._st7036 = st7036
        self._register = 'instruction'
        self._mode = 'w'
        self._reset_in_progress = False
        self._display_event = threading.Event()
        self._clock_thread = threading.Thread(target=self.switch_frame)
        self._clock_thread.daemon = True
        self._clock_thread.start()
        self._frame_thread = threading.Thread(target=self.display_frame)
        self._frame_thread.daemon = True
        self._frame_thread.start()

    def switch_frame(self):
        while True:
            for i in range(0, 64):
                self._display_event.set()
                time.sleep(0.007) # approx. 7 ms
            self._st7036.toggle_cursor_high_state()

    def display_frame(self):
        while True:
            self._display_event.wait()
            self._st7036.refresh_display()
            self._display_event.clear()

    def spi_xfer(self, input_bytes):
        assert len(input_bytes) == 1
        f = self._st7036.find_instruction(input_bytes[0], self._register, self._mode)
        f(input_bytes[0])
        return [self._st7036.data_register]

    def gpio_output(self, pin, level):
        if pin == Controller.RESET_PIN:
            if self._reset_in_progress and level == Controller.GPIO_HIGH:
                self._reset_in_progress = False
                self._st7036.reset()
            else:
                self._reset_in_progress = True
        elif pin == Controller.REGISTER_SELECT_PIN:
            if level == Controller.GPIO_HIGH:
                self._register = 'data'
            else:
                self._register = 'instruction'
        elif pin == Controller.READ_WRITE_PIN:
            if level == Controller.GPIO_HIGH:
                self._mode = 'r'
            else:
                self._mode = 'w'

class ST7036(object):
    CGROM = CHARACTER_MAP
    DDRAM_SIZE = 80 # bytes
    CGRAM_SIZE = 64 # bytes
    ICON_RAM_SIZE = 80 # bits

    CHARACTER_WIDTH = 5 # pixels
    CHARACTER_HEIGHT = 8 # pixels

    USER_DEFINED_CHARACTERS = 8

    DDRAM_LAYOUT = { 1: [range(0x00, 0x50)]
                   , 2: [range(0x00, 0x28), range(0x40, 0x68)]
                   , 3: [range(0x00, 0x10), range(0x10, 0x20), range(0x20, 0x30)]
                   }

    def __init__(self, display, extended_mode=True):
        self._extended_mode = extended_mode
        if display.lines not in ST7036.DDRAM_LAYOUT.keys():
            raise ValueError('Can only handle 1, 2, or 3 lines devices')
        if display.lines in (1, 2) and display.columns > 20:
            raise ValueError('Can only handle 20 columns when displaying 1 or 2 lines')
        if display.lines == 3 and display.columns > 16:
            raise ValueError('Can only handle 16 columns when displaying 3 lines')
        self._display_changed = False
        self._display = display
        self._ddram = [0x00] * ST7036.DDRAM_SIZE
        self._cgram = [0x00] * ST7036.CGRAM_SIZE
        self._icon_ram = [0x00] * (ST7036.ICON_RAM_SIZE // 5) # only 5 bits are used per row)
        self._cursor_offset = 0
        self._cursor_high_state = False # for blink

        self._data_register = 0
        self._instruction_register = 0
        self._busy_flag = 0
        self._address_counter = 0
        self._selected_memory = None

        self._display_on = False
        self._instruction_set = 0

        self._pixels = [[False] * (self._display.columns * ST7036.CHARACTER_WIDTH) for y in range(self._display.lines * ST7036.CHARACTER_HEIGHT)]

    def reset(self):
        self._busy_flag = True
        # 1.
        self.clear_display(0)
        # 2.
        self._data_length = 8 # DL bit in function set: high = 8, low = 4
        self._n_bit = self._display.lines == 3
        self._dh_bit = False
        self._instruction_set = 0
        # 3.
        self._display_on = False
        self._cursor_on = False
        self._cursor_blink = False
        # 4.
        self._cursor_direction = 1 # correspond to I/D register: high = 1, low = -1
        self._display_offset = 0
        self._display_shift = False
        # 6.
        self._icon_visible = False
        # 7.
        self._bias = False
        self._booster_on = False
        self._follower_on = False
        self.contrast = 0b100000
        self._v0_amplified_ration = 0b010
        # 8.
        self._ud_bit = False

        self.update_row_span()

        self._busy_flag = False

    @property
    def data_register(self):
        return self._data_register

    def find_instruction(self, b, register='instruction', mode='w'):
        if register == 'data': # data
            if mode == 'r':
                return self.read_data
            else:
                return self.write_data
        else: # instructions
            if mode == 'r':
                return self.read_busy_flag_and_address

            if not self._extended_mode:
                if (b >> 7) & 1: return self.set_ddram_address
                if (b >> 6) & 1: return self.set_cgram_address
                if (b >> 5) & 1: return self.set_function
                if (b >> 4) & 1: return self.shift_cursor_or_display
                if (b >> 3) & 1: return self.switch_display_on_off
                if (b >> 2) & 1: return self.set_entry_mode
                if (b >> 1) & 1: return self.return_home
                if  b       & 1: return self.clear_display
            else:
                if (b >> 7) & 1: return self.set_ddram_address
                if (b >> 6) & 1:
                    if self._instruction_set == 0:
                        return self.set_cgram_address
                    elif self._instruction_set == 1:
                        if (b >> 4) & 0b111 == 0b111: return self.set_contrast_low
                        if (b >> 4) & 0b110 == 0b110: return self.control_follower
                        if (b >> 4) & 0b101 == 0b101: return self.set_power_icon_contrast_high
                        if (b >> 4) & 0b100 == 0b100: return self.set_icon_address
                    elif self._instruction_set == 2:
                        raise ValueError('reserved instruction')
                    else:
                        raise RuntimeError('Unknown instruction table')
                if (b >> 5) & 1: return self.set_function
                if (b >> 4) & 1:
                    if self._instruction_set == 0:
                        return self.shift_cursor_or_display
                    elif self._instruction_set == 1:
                        if (b | 0b00001001) & 0b00011101: return self.set_bias
                    elif self._instruction_set == 2:
                        return self.set_double_height_position
                    else:
                        raise RuntimeError('Unknown instruction table')
                if (b >> 3) & 1: return self.switch_display_on_off
                if (b >> 2) & 1: return self.set_entry_mode
                if (b >> 1) & 1: return self.return_home
                if  b       & 1: return self.clear_display
                raise ValueError('Unknown instruction {b:08b} (register: {register}, mode: {mode})'.format(b=b, register=register, mode=mode))

    def _get_user_defined_character(self, charcode):
        assert charcode in range(0, ST7036.USER_DEFINED_CHARACTERS)
        cgram_base_address = charcode << 3
        cgram_lines = self._cgram[cgram_base_address:cgram_base_address + ST7036.CHARACTER_HEIGHT]
        return [ [ '1' == c for c in "{:05b}".format(line) ] for line in cgram_lines ]

    def _blit_character(self, character_x, character_y, pixels, character):
        pixel_y = character_y * ST7036.CHARACTER_HEIGHT
        for line in character:
            pixel_x = character_x * ST7036.CHARACTER_WIDTH
            for pixel in line:
                pixels[pixel_y][pixel_x] = pixel
                pixel_x += 1
            pixel_y += 1

    def _draw_cursor(self, character_x, character_y, pixels):
        if self._cursor_blink and self._cursor_high_state:
            lines = [(character_y + 1) * ST7036.CHARACTER_HEIGHT - 1]
        else:
            lines = range(character_y * ST7036.CHARACTER_HEIGHT, (character_y + 1) * ST7036.CHARACTER_HEIGHT)
        for pixel_y in lines:
            for pixel_x in range(character_x * ST7036.CHARACTER_WIDTH, (character_x + 1) * ST7036.CHARACTER_WIDTH):
                pixels[pixel_y][pixel_x] = True

    def _refresh_pixels(self, new_pixels):
        for y, line in enumerate(new_pixels):
            for x, pixel in enumerate(line):
                if self._pixels[y][x] != pixel:
                    self._display.set_pixel(x, y, pixel)

    def refresh_display(self):
        if not self._display_changed:
            return
        # Initialize an empty framebuffer
        new_pixels = [[False] * (self._display.columns * ST7036.CHARACTER_WIDTH) for y in range(self._display.lines * ST7036.CHARACTER_HEIGHT)]
        for y in range(self._display.lines):
            ddram_addresses = itertools.cycle(ST7036.DDRAM_LAYOUT[self._display.lines][y])
            print('shift: ', self._display_offset)
            for x, ddram_address in enumerate(itertools.islice(ddram_addresses, self._display_offset, self._display.columns + self._display_offset)):
                charcode = self._ddram[ddram_address]
                # XXX: implement cgram switches
                if charcode in range(0, ST7036.USER_DEFINED_CHARACTERS):
                    character = self._get_user_defined_character(charcode)
                else:
                    character = CHARACTER_MAP[charcode]
                self._blit_character(x, y, new_pixels, character)
                if self._cursor_on and self._address_counter == ddram_address:
                    self._draw_cursor(x, y, new_pixels)
        self._refresh_pixels(new_pixels)
        self._pixels = new_pixels
        self._display_changed = False

    def set_ddram(self, offset, value):
        self._ddram[offset] = value
        self._display_changed = True

    def set_cgram(self, offset, value):
        self._cgram[offset] = value
        self._display_changed = True

    def set_icon_ram(self, offset, value):
        self._icon_ram[offset] = value & 0b11111
        self._display_changed = True

    def clear_display(self, db):
        for offset in range(0, ST7036.DDRAM_SIZE):
            self.set_ddram(offset, 0x20) # space code
        self._address_counter = 0
        self._cursor_offset = 0
        self._cursor_direction = 1

    def return_home(self, db):
        self._address_counter = 0
        self._cursor_offset = 0
        self._display_offset = 0

    def set_entry_mode(self, db):
        self._display_shift = db & 0b1 == 0b1
        self._cursor_direction = 1 if (db >> 1 & 0b1) == 0b1 else -1

    @property
    def display_on(self):
        return self._display_on

    @display_on.setter
    def display_on(self, value):
        if value and not self._display_on:
            self._display.turn_display_on()
        if not value and self._display_on:
            self._display.turn_display_off()
        self._display_on = value

    @property
    def cursor_on(self):
        return self._cursor_on

    @cursor_on.setter
    def cursor_on(self, value):
        self._cursor_on = value

    @property
    def cursor_blink(self):
        return self._cursor_blink

    @cursor_blink.setter
    def cursor_blink(self, value):
        self._cursor_blink = value

    def toggle_cursor_high_state(self):
        self._cursor_high_state = not self._cursor_high_state
        if self._cursor_blink:
            self._display_changed = True

    def switch_display_on_off(self, db):
        self.display_on = db & 0b100 == 0b100
        self.cursor_on = db & 0b10 == 0b10
        self.cursor_blink = db & 0b1 == 0b1

    @property
    def display_offset(self):
        return self._display_offset

    @display_offset.setter
    def display_offset(self, value):
        self._display_offset = value % self._display.columns
        self._display_changed = True

    def cursor_left(self):
        self._write_command(COMMAND_SCROLL, 0)

    def cursor_right(self):
        self._write_command(COMMAND_SCROLL | (1 << 2), 0)

    def shift_left(self):
        self._write_command(COMMAND_SCROLL | (1 << 3), 0) # 0x18

    def shift_right(self):
        self._write_command(COMMAND_SCROLL | (1 << 3) | (1 << 2), 0) # 0x1C

    def shift_cursor_or_display(self, db):
        shift = 1 if db >> 2 & 0b1 == 0b1 else -1
        if db & 0b1000 == 0b1000: # shift display
            self.display_offset -= shift
        else: # shift cursor
            self._address_counter += shift

    @property
    def n_bit(self):
        return self._n_bit

    @n_bit.setter
    def n_bit(self, value):
        self._n_bit = value
        self.update_row_span()

    @property
    def dh_bit(self):
        return self._dh_bit

    @dh_bit.setter
    def dh_bit(self, value):
        self._dh_bit = value
        self.update_row_span()

    @property
    def ud_bit(self):
        return self._ud_bit

    @ud_bit.setter
    def ud_bit(self, value):
        self._ud_bit = value
        self.update_row_span()

    @property
    def row_span(self):
        return self._row_span

    @row_span.setter
    def row_span(self, value):
        self._row_span = value
        self._display_changed = True

    def update_row_span(self):
        if not self._extended_mode:
            self.row_span = [1] * self._display.lines
        else:
            if self._display.lines == 3:
                if not self.n_bit:
                    raise ValueError('N must be high when N3 is high')
                if not self.dh_bit:
                    self.row_span = [1, 1, 1]
                elif not self.ud_bit:
                    self.row_span = [1, 2]
                else:
                    self.row_span = [2, 1]
            else:
                if self.n_bit and self.dh_bit:
                    raise ValueError('N=high DH=high forbidden')
                elif not self.dh_bit and self.n_bit:
                    self.row_span = [1] * self._display.lines
                else:
                    self.row_span = [2]

    def set_function(self, db):
        if db & 0b10000 == 0b10000: # DL bit
            self._data_length = 8
        else:
            self._data_length = 4
        self.n_bit = db & 0b1000 == 0b1000 # N bit
        self._instruction_set = db & 0b11
        if self._instruction_set not in (0, 1, 2):
            raise ValueError('Reserved instruction set')

    def set_double_height_position(self, db):
        self.ud_bit = db & 0b1000 == 0b1000

    def set_cgram_address(self, db):
        self._address_counter = db & 0b111111
        self._selected_memory = 'cgram'

    def set_ddram_address(self, db):
        self._address_counter = db & 0b1111111
        self._selected_memory = 'ddram'

    def read_busy_flag_and_address(self):
        self._data_register = (self._busy_flag << 7) | self._address_counter

    def write_data(self, db):
        if self._selected_memory == 'ddram':
            self.set_ddram(self._address_counter, db)
        elif self._selected_memory == 'cgram':
            self.set_cgram(self._address_counter, db)
        elif self._selected_memory == 'icon ram':
            self.set_icon_ram(self._address_counter, db)
        else:
            raise RuntimeError('Unknown selected memory')
        if self._display_shift:
            self.display_offset += self._cursor_direction
        self._address_counter += self._cursor_direction

    def read_data(self, db):
        if self._selected_memory == 'ddram':
            self._data_register = (self._busy_flag << 7) | self._ddram[self._address_counter]
        elif self._selected_memory == 'cgram':
            self._data_register = (self._busy_flag << 7) | self._cgram[self._address_counter]
        else:
            raise RuntimeError('Unknown selected memory')
        # XXX: compare with hardware
        self._address_counter += self._cursor_direction

    def set_bias(self, db):
        if self._display.lines == 3:
           if db & 0b1 == 0b0:
               raise ValueError('FX must be fixed high')
        else:
           if db & 0b1 == 0b1:
               raise ValueError('FX must be fixed low')
        self._bias = db & 0b1000 == 0b1000

    def set_icon_address(self, db):
        self._address_counter = db & 0b1111
        self._selected_memory = 'icon ram'

    @property
    def icon_visible(self):
        return self._icon_visible

    @icon_visible.setter
    def icon_visible(self, value):
        self._icon_visible = value
        self._display_changed = True

    @property
    def contrast(self):
        return self._contrast

    @contrast.setter
    def contrast(self, value):
        self._contrast = value
        self._display.change_contrast(value)

    def set_power_icon_contrast_high(self, db):
        self.icon_visible = db & 0b1000 == 0b1000
        self._booster_on = db & 0b100 == 0b100
        self.contrast = (db & 0b11) << 4 | (self.contrast & 0b001111)

    def control_follower(self, db):
        self._follower_on = db & 0b1000 == 0b1000
        self._v0_amplified_ration = db & 0b111

    def set_contrast_low(self, db):
        self.contrast = (self.contrast & 0b110000) | (db & 0b1111)
