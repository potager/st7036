from character_map import CHARACTER_MAP


class Display(object):
    @property
    def lines(self):
        return 3

    def set_pixel(self, XXX):
        pass

    def turn_display_on(self):
        pass

    def turn_display_off(self):
        pass

    def change_contrast(self, value):

class ST7036(object):
    CGROM = CHARACTER_MAP
    DDRAM_SIZE = 80 # bytes
    CGRAM_SIZE = 64 # bytes
    ICON_RAM_SIZE = 80 # bits

    DDRAM_LAYOUT = { 1: [range(0x00, 0x50)]
                   , 2: [range(0x00, 0x28), range(0x40, 0x68)]
                   , 3: [range(0x00, 0x10), range(0x10, 0x20), range(0x20, 0x30)]
                   }

    def __init__(self, extended_mode=True, display):
        self._extended_mode = extended_mode
        if display.lines not in DDRAM_LAYOUT.keys():
            raise ValueError('Can only handle 1, 2, or 3 lines devices')
        self._display_changed = False
        self._display = display
        self._ddram = [0x00] * ST7036.DDRAM_SIZE
        self._cgram = [0x00] * ST7036.CGRAM_SIZE
        self._icon_ram = [False] * ST7036.ICON_RAM_SIZE
        self._cursor_offset = 0

        self._opr1 = 0 #?
        self._opr2 = 0 #?
        self._data_register = 0
        self._instruction_register = 0
        self._busy_flag = 0
        self._address_counter = 0
        self._selected_memory = None

    def reset(self):
        self._busy_flag = True
        # 1.
        self.clear_display()
        # 2.
        self._data_length = 8 # DL bit in function set: high = 8, low = 4
        self._n_bit = False
        self._dh_bit = False
        self._instruction_set = 0
        # 3.
        self._display_on = False
        self._cursor_on = False
        self._cursor_blink = False
        # 4.
        self._cursor_direction = 1 # correspond to I/D register: high = 1, low = -1
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

    def find_instruction(self, b):
        if self.register_select_pin_value: # data
            if self.read_write_pin_value:
                return self.read_data
            return self.write_data
        else: # instructions
            if self.read_write_pin_value:
                return self.read_busy_flag_and_address
            if not self._extended_mode:
                if  b       & 1: return clear_display
                if (b >> 1) & 1: return return_home
                if (b >> 2) & 1: return set_entry_mode
                if (b >> 3) & 1: return switch_display_on_off
                if (b >> 4) & 1: return shift_cursor_or_display
                if (b >> 5) & 1: return set_function
                if (b >> 7) & 1: return set_cgram_address
                if (b >> 8) & 1: return set_ddram_address
            else:
                if  b       & 1: return clear_display
                if (b >> 1) & 1: return return_home
                if (b >> 2) & 1: return set_entry_mode
                if (b >> 3) & 1: return swich_display_on_off
                if (b >> 5) & 1: return set_function
                if (b >> 8) & 1: return set_ddram_address
                if self._instruction_set == 0:    # IS[2:1] == [0, 0]
                    if (b >> 4) & 1: return cursor_or_display_shift
                    if (b >> 6) & 1: return set_cgram_address
                elif self._instruction_set == 1:  # IS[2:1] == [0, 1]
                    if (b | 0b00001001) & 0b00011101: return set_bias
                    if (b | 0b00001111) & 0b01001111: return set_icon_address
                    if (b | 0b00001111) & 0b01011111: return set_power_icon_contrast_high
                    if (b | 0b00001111) & 0b01101111: return control_follower
                    if (b | 0b00001111) & 0b01111111: return set_contrast_low
                elif self._instruction_set == 2:  # IS[2:1] == [1, 0]
                    if (b >> 4) & 1: return set_double_height_position
                    if (b >> 6) & 1: raise ValueError('reserved instruction')
                elif self._instruction_set == 3:  # IS[2:1] == [1, 1]
                    raise ValueError('reserved instruction table')
                else:
                    raise RuntimeError('Unknown instruction table')
                raise ValueError('Unknown instruction')

    def set_ddram(offset, value):
        self._ddram[offset] = value
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
        self._cursor_direction = -(db & 0b1) * -1

    @property
    def display_on(self):
        return self._display_on

    @display_on.setter
    def display_on(self, value):
        if value and not self._display_on:
            self.display.turn_display_on()
        if not value and self._display_on:
            self.display.turn_display_off()
        self._display_on = value

    @property
    def cursor_on(self):
        return self._cursor_on

    @cursor_on.setter
    def cursor_on(self, value)
        self._cursor_on = value

    @property
    def cursor_blink(self):
        return self._cursor_blink

    @cursor_blink.setter
    def cursor_blink(self, value)
        self._cursor_blink = value

    def switch_display_on_off(self, db):
        self.display_on = db & 0b100 == 0b100
        self.cursor_on = db & 0b10 == 0b10
        self.cursor_blink = db & 0b1 == 0b1

    @property
    def display_offset(self):
        return self._display_offset

    @display_offset.setter
    def display_offset(self, value):
        self._display_offset = value
        self._display_changed = True

    def shift_cursor_or_display(self, db):
        if db & 0b1000 == 0b1000: # Screen
            self._address_counter += -((db & 0b100) >> 2) * -1
        else: # cursor
            self.display_offset = -((db & 0b100) >> 2) * -1

    @property
    def n_bit(self):
        return self._n_bit

    @display_offset.setter
    def n_bit(self, value):
        self._n_bit = value
        self.update_row_span()

    @property
    def dh_bit(self):
        return self._dh_bit

    @display_offset.setter
    def dh_bit(self, value):
        self._dh_bit = value
        self.update_row_span()

    @property
    def ud_bit(self):
        return self._ud_bit

    @display_offset.setter
    def ud_bit(self, value):
        self._ud_bit = value
        self.update_row_span()

    @property
    def row_span(self):
        return self._row_span

    @display_offset.setter
    def row_span(self, value):
        self._row_span = value
        self._display_changed = True

    def update_row_span(self):
        if not self._extended_mode:
            self.row_span = [1] * self.display.lines
        else:
            if self.display.lines == 3:
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
                elif not self.dh_bit and self._n_bit:
                    self.row_span = [1] * self.display.lines
                else:
                    self.row_span = [2]

    def set_function(self, db):
        if db & 0b10000 == 0b10000: # DL bit
            self._data_length = 8
        else:
            self._data_length = 4
        self.n_bit = db & 0b1000 == 0b1000 # N bit
        self._instruction_set = db & 0b11

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
        self._address_counter += self._cursor_direction

    def read_data(self, db):
        if self._selected_memory == 'ddram':
            self._data_register = (self._busy_flag << 7) | self._ddram[self._address_counter]
        elif self._selected_memory == 'cgram':
            self._data_register = (self._busy_flag << 7) | self._cgram[self._address_counter]
        else:
            raise RuntimeError('Unknown selected memory')
        self._address_counter += self._cursor_direction

    def set_bias(self, db):
        if self.display.lines == 3:
           if db & 0b1 == 0b0
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
        return self._icon_visible

    @contrast.setter
    def contrast(self, value):
        self._contrast = value
        self.display.change_contrast(value)

    def set_power_icon_contrast_high(self, db):
        self.icon_visible = db & 0b1000 == 0b1000
        self._booster_on = db & 0b100 = 0b100
        self.contrast |= (db & 0b11) << 4

    def control_follower(self, db):
        self._follower_on = db & 0b1000 == 0b1000
        self._v0_amplified_ration = db & 0b111

    def set_contrast_low(self, db):
        self.contrast |= db & 0b1111
