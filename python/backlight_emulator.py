import colorsys

display = None

NUM_LEDS = 6
STEP_VALUE = 16

leds = [0x00] * 18  # B G R, B G R, B G R, B G R, B G R, B G R

# taken from sn3218
default_gamma_table = [int(pow(255, float(i - 1) / 255)) for i in range(256)]
channel_gamma_table = [default_gamma_table] * 18

def channel_gamma(channel, gamma_table):
    """ 
    Overrides the gamma table for a single channel.

    Args:
        channel (int): channel number
        gamma_table (list): list of 256 gamma correction values
    Raises:
        TypeError: if channel is not an integer.
        ValueError: if channel is not in the range 0..17.
        TypeError: if gamma_table is not a list.
    """ 
    global channel_gamma_table

    if type(channel) is not int:
        raise TypeError("channel must be an integer")

    if channel not in range(18):
        raise ValueError("channel be an integer in the range 0..17")

    if type(gamma_table) is not list or len(gamma_table) != 256:
        raise TypeError("gamma_table must be a list of 256 integers")

    channel_gamma_table[channel] = gamma_table  


# set gamma correction for backlight to normalise brightness
g_channel_gamma = [int(value / 1.6) for value in default_gamma_table]
r_channel_gamma = [int(value / 1.4) for value in default_gamma_table]

for x in range(0, 18, 3):
    channel_gamma(x + 1, g_channel_gamma)
    channel_gamma(x + 2, r_channel_gamma)

def graph_set_led_state():
    ...

def graph_set_led_polarity():
    ...

def graph_set_led_duty():
    ...


def use_rbg():
    """
    Swaps the Green and Blue channels on the LED backlight
  
    Use if you have a first batch Display-o-Tron 3K
    """
    pass


def graph_off():
    pass


def set_graph(percentage):
    """
    Lights a number of bargraph LEDs depending upon value
    
    Args:
        value (float): percentage between 0.0 and 1.0

    Todo:
        Reimplement using CAP
    """
    ...


def set(index, value):
    """
    Set a specific LED to a value
    
    Args:
        index (int): index of the LED from 0 to 18
        value (int): brightness value from 0 to 255
    """
    index = index if isinstance(index, list) else [index]
    for i in index:
        leds[i] = value
    update()


def set_bar(index, value):
    """
    Set a value or values to one or more LEDs
    
    Args:
        index (int): starting index
        value (int or list): a single int, or list of brightness values from 0 to 255
    """
    pass


def hue_to_rgb(hue):
    """
    Converts a hue to RGB brightness values
    
    Args:
        hue (float): hue value between 0.0 and 1.0
    """
    rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)

    return [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)]


def hue(hue):
    """
    Sets the backlight LEDs to supplied hue
    
    Args:
        hue (float): hue value between 0.0 and 1.0
    """
    col_rgb = hue_to_rgb(hue)
    rgb(col_rgb[0], col_rgb[1], col_rgb[2])


def sweep(hue, sweep_range=0.0833):
    """
    Sets the backlight LEDs to a gradient centered on supplied hue
    
    Supplying zero to range would be the same as hue()
    
    Args:
        hue (float): hue value between 0.0 and 1.0
        range (float): range value to deviate the left and right hue
    """
    global leds
    for x in range(0, 18, 3):
        rgb = hue_to_rgb((hue + (sweep_range * (x / 3))) % 1)
        rgb.reverse()
        leds[x:x + 3] = rgb
    update()


def left_hue(hue):
    """
    Set the left backlight to supplied hue
    
    Args:
        hue (float): hue value between 0.0 and 1.0
    """
    col_rgb = hue_to_rgb(hue)
    left_rgb(col_rgb[0], col_rgb[1], col_rgb[2])
    update()


def mid_hue(hue):
    """
    Set the middle backlight to supplied hue
    
    Args:
        hue (float): hue value between 0.0 and 1.0
    """
    col_rgb = hue_to_rgb(hue)
    mid_rgb(col_rgb[0], col_rgb[1], col_rgb[2])
    update()


def right_hue(hue):
    """
    Set the right backlight to supplied hue
    
    Args:
        hue (float): hue value between 0.0 and 1.0
    """
    col_rgb = hue_to_rgb(hue)
    right_rgb(col_rgb[0], col_rgb[1], col_rgb[2])
    update()


def left_rgb(r, g, b):
    """
    Set the left backlight to supplied r, g, b colour
    
    Args:
        r (int): red value between 0 and 255
        g (int): green value between 0 and 255
        b (int): blue value between 0 and 255
    """
    single_rgb(0, r, g, b, False)
    single_rgb(1, r, g, b, False)
    update()


def mid_rgb(r, g, b):
    """
    Set the middle backlight to supplied r, g, b colour
    
    Args:
        r (int): red value between 0 and 255
        g (int): green value between 0 and 255
        b (int): blue value between 0 and 255
    """
    single_rgb(2, r, g, b, False)
    single_rgb(3, r, g, b, False)
    update()


def right_rgb(r, g, b):
    """
    Set the right backlight to supplied r, g, b colour
    
    Args:
        r (int): red value between 0 and 255
        g (int): green value between 0 and 255
        b (int): blue value between 0 and 255
    """
    single_rgb(4, r, g, b, False)
    single_rgb(5, r, g, b, False)
    update()


def single_rgb(led, r, g, b, auto_update=True):
    global leds
    leds[(led * 3)] = b
    leds[(led * 3) + 1] = g
    leds[(led * 3) + 2] = r
    if auto_update:
        update()


def rgb(r, g, b):
    """
    Sets all backlights to supplied r, g, b colour
    
    Args:
        r (int): red value between 0 and 255
        g (int): green value between 0 and 255
        b (int): blue value between 0 and 255
    """
    global leds
    leds = [b, g, r] * 6
    update()


def off():
    """
    Turns off the backlight.
    """
    rgb(0, 0, 0)


def update():
    """
    Update backlight with changes to the LED buffer
    """
    # led order is B G R
    for led_index in range(0, 6):
        display.set_backlight_color(led_index, leds[(led_index * 3) + 2], leds[(led_index * 3) + 1], leds[led_index * 3])
