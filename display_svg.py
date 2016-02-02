from gi.repository import Gtk
from gi.repository import WebKit

import itertools
import random

VALID_DDRAM_ADDRESSES = list(range(0x00, 0x30))

class Example(Gtk.Window):
    def __init__(self):
        super(Example, self).__init__()
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
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def on_click_run(self, button):
        for i in range(0, 20):
            self.set_pixel_state(random.choice(VALID_DDRAM_ADDRESSES), random.randint(0, 7), random.randint(0, 4), on=True)

    def set_pixel_state(self, ddram_address, row, column, on=True):
        if ddram_address not in VALID_DDRAM_ADDRESSES:
            raise ValueError('DDRAM address outside display')
        if on:
            opacity = 1
        else:
            opacity = 0
        self.display.execute_script("document.getElementById('ddram-0x{ddram_address:02x}-pixel-0x{row:02x}-b{column:x}').style.fillOpacity = {opacity};".format(ddram_address=ddram_address, row=row, column=column, opacity=opacity))


def main():
    app = Example()
    Gtk.main()

if __name__ == "__main__":
    main()
