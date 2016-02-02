#!/usr/bin/python3
# Python character encoding for the ST7036 LCD Display
#
# Unicode characters picked according to the table in
# http://www.lcd-module.de/eng/pdf/zubehoer/st7036.pdf
#
# Written in 2016 by Lunar <lunar@anargeek.net>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# The CC0 Public Domain Dedication is available at
# <http://creativecommons.org/publicdomain/zero/1.0/>.

import codecs

USER_DEFINED_CHARACTER_0 = 0xEFF80
USER_DEFINED_CHARACTER_1 = 0xEFF81
USER_DEFINED_CHARACTER_2 = 0xEFF82
USER_DEFINED_CHARACTER_3 = 0xEFF83
USER_DEFINED_CHARACTER_4 = 0xEFF84
USER_DEFINED_CHARACTER_5 = 0xEFF85
USER_DEFINED_CHARACTER_6 = 0xEFF86
USER_DEFINED_CHARACTER_7 = 0xEFF87

decoding_map = { 0b00000000: USER_DEFINED_CHARACTER_0,
                 0b00000001: USER_DEFINED_CHARACTER_1,
                 0b00000010: USER_DEFINED_CHARACTER_2,
                 0b00000011: USER_DEFINED_CHARACTER_3,
                 0b00000100: USER_DEFINED_CHARACTER_4,
                 0b00000101: USER_DEFINED_CHARACTER_5,
                 0b00000110: USER_DEFINED_CHARACTER_6,
                 0b00000111: USER_DEFINED_CHARACTER_7,
                 0b00001000: 0x2190, # LEFTWARDS ARROW
                 0b00001001: 0x250C, # BOX DRAWINGS LIGHT DOWN AND RIGHT
                 0b00001010: 0x2510, # BOX DRAWINGS LIGHT DOWN AND LEFT
                 0b00001011: 0x2514, # BOX DRAWINGS LIGHT UP AND RIGHT
                 0b00001100: 0x2518, # BOX DRAWINGS LIGHT UP AND LEFT
                 0b00001101: 0x00B7, # MIDDLE DOT
                 0b00001110: 0x00AE, # REGISTERED SIGN
                 0b00001111: 0x00A9, # COPYRIGHT SIGN
                 0b00010000: 0x2122, # TRADE MARK SIGN
                 0b00010001: 0x2020, # DAGGER
                 0b00010010: 0x00A7, # SECTION SIGN
                 0b00010011: 0x00B6, # PILCROW SIGN
                 0b00010100: 0x0393, # GREEK CAPITAL LETTER GAMMA
                 0b00010101: 0x0394, # GREEK CAPITAL LETTER DELTA
                 0b00010110: 0x0398, # GREEK CAPITAL LETTER THETA
                 0b00010111: 0x039B, # GREEK CAPITAL LETTER LAMDA
                 0b00011000: 0x039E, # GREEK CAPITAL LETTER XI
                 0b00011001: 0x03A0, # GREEK CAPITAL LETTER PI
                 0b00011010: 0x03A3, # GREEK CAPITAL LETTER SIGMA
                 0b00011011: 0x03D2, # GREEK UPSILON WITH HOOK SYMBOL
                 0b00011100: 0x03A6, # GREEK CAPITAL LETTER PHI
                 0b00011101: 0x03A8, # GREEK CAPITAL LETTER PSI
                 0b00011110: 0x03A9, # GREEK CAPITAL LETTER OMEGA
                 0b00011111: 0x03B1, # GREEK SMALL LETTER ALPHA
                 0b00100000: 0x0020, # SPACE
                 0b00100001: 0x0021, # EXCLAMATION MARK
                 0b00100010: 0x0022, # QUOTATION MARK
                 0b00100011: 0x0023, # NUMBER SIGN
                 0b00100100: 0x0024, # DOLLAR SIGN
                 0b00100101: 0x0025, # PERCENT SIGN
                 0b00100110: 0x0026, # AMPERSAND
                 0b00100111: 0x0027, # APOSTROPHE
                 0b00101000: 0x0028, # LEFT PARENTHESIS
                 0b00101001: 0x0029, # RIGHT PARENTHESIS
                 0b00101010: 0x002A, # ASTERISK
                 0b00101011: 0x002B, # PLUS SIGN
                 0b00101100: 0x002C, # COMMA
                 0b00101101: 0x002D, # HYPHEN-MINUS
                 0b00101110: 0x002E, # FULL STOP
                 0b00101111: 0x002F, # SOLIDUS
                 0b00110000: 0x0030, # DIGIT ZERO
                 0b00110001: 0x0031, # DIGIT ONE
                 0b00110010: 0x0032, # DIGIT TWO
                 0b00110011: 0x0033, # DIGIT THREE
                 0b00110100: 0x0034, # DIGIT FOUR
                 0b00110101: 0x0035, # DIGIT FIVE
                 0b00110110: 0x0036, # DIGIT SIX
                 0b00110111: 0x0037, # DIGIT SEVEN
                 0b00111000: 0x0038, # DIGIT EIGHT
                 0b00111001: 0x0039, # DIGIT NINE
                 0b00111010: 0x003A, # COLON
                 0b00111011: 0x003B, # SEMICOLON
                 0b00111100: 0x003C, # LESS-THAN SIGN
                 0b00111101: 0x003D, # EQUALS SIGN
                 0b00111110: 0x003E, # GREATER-THAN SIGN
                 0b00111111: 0x003F, # QUESTION MARK
                 0b01000000: 0x0040, # COMMERCIAL AT
                 0b01000001: 0x0041, # LATIN CAPITAL LETTER A
                 0b01000010: 0x0042, # LATIN CAPITAL LETTER B
                 0b01000011: 0x0043, # LATIN CAPITAL LETTER C
                 0b01000100: 0x0044, # LATIN CAPITAL LETTER D
                 0b01000101: 0x0045, # LATIN CAPITAL LETTER E
                 0b01000110: 0x0046, # LATIN CAPITAL LETTER F
                 0b01000111: 0x0047, # LATIN CAPITAL LETTER G
                 0b01001000: 0x0048, # LATIN CAPITAL LETTER H
                 0b01001001: 0x0049, # LATIN CAPITAL LETTER I
                 0b01001010: 0x004A, # LATIN CAPITAL LETTER J
                 0b01001011: 0x004B, # LATIN CAPITAL LETTER K
                 0b01001100: 0x004C, # LATIN CAPITAL LETTER L
                 0b01001101: 0x004D, # LATIN CAPITAL LETTER M
                 0b01001110: 0x004E, # LATIN CAPITAL LETTER N
                 0b01001111: 0x004F, # LATIN CAPITAL LETTER O
                 0b01010000: 0x0050, # LATIN CAPITAL LETTER P
                 0b01010001: 0x0051, # LATIN CAPITAL LETTER Q
                 0b01010010: 0x0052, # LATIN CAPITAL LETTER R
                 0b01010011: 0x0053, # LATIN CAPITAL LETTER S
                 0b01010100: 0x0054, # LATIN CAPITAL LETTER T
                 0b01010101: 0x0055, # LATIN CAPITAL LETTER U
                 0b01010110: 0x0056, # LATIN CAPITAL LETTER V
                 0b01010111: 0x0057, # LATIN CAPITAL LETTER W
                 0b01011000: 0x0058, # LATIN CAPITAL LETTER X
                 0b01011001: 0x0059, # LATIN CAPITAL LETTER Y
                 0b01011010: 0x005A, # LATIN CAPITAL LETTER Z
                 0b01011011: 0x005B, # LEFT SQUARE BRACKET
                 0b01011100: 0x005C, # REVERSE SOLIDUS
                 0b01011101: 0x005D, # RIGHT SQUARE BRACKET
                 0b01011110: 0x005E, # CIRCUMFLEX ACCENT
                 0b01011111: 0x005F, # LOW LINE
                 0b01100000: 0x0060, # GRAVE ACCENT
                 0b01100001: 0x0061, # LATIN SMALL LETTER A
                 0b01100010: 0x0062, # LATIN SMALL LETTER B
                 0b01100011: 0x0063, # LATIN SMALL LETTER C
                 0b01100100: 0x0064, # LATIN SMALL LETTER D
                 0b01100101: 0x0065, # LATIN SMALL LETTER E
                 0b01100110: 0x0066, # LATIN SMALL LETTER F
                 0b01100111: 0x0067, # LATIN SMALL LETTER G
                 0b01101000: 0x0068, # LATIN SMALL LETTER H
                 0b01101001: 0x0069, # LATIN SMALL LETTER I
                 0b01101010: 0x006A, # LATIN SMALL LETTER J
                 0b01101011: 0x006B, # LATIN SMALL LETTER K
                 0b01101100: 0x006C, # LATIN SMALL LETTER L
                 0b01101101: 0x006D, # LATIN SMALL LETTER M
                 0b01101110: 0x006E, # LATIN SMALL LETTER N
                 0b01101111: 0x006F, # LATIN SMALL LETTER O
                 0b01110000: 0x0070, # LATIN SMALL LETTER P
                 0b01110001: 0x0071, # LATIN SMALL LETTER Q
                 0b01110010: 0x0072, # LATIN SMALL LETTER R
                 0b01110011: 0x0073, # LATIN SMALL LETTER S
                 0b01110100: 0x0074, # LATIN SMALL LETTER T
                 0b01110101: 0x0075, # LATIN SMALL LETTER U
                 0b01110110: 0x0076, # LATIN SMALL LETTER V
                 0b01110111: 0x0077, # LATIN SMALL LETTER W
                 0b01111000: 0x0078, # LATIN SMALL LETTER X
                 0b01111001: 0x0079, # LATIN SMALL LETTER Y
                 0b01111010: 0x007A, # LATIN SMALL LETTER Z
                 0b01111011: 0x007B, # LEFT CURLY BRACKET
                 0b01111100: 0x007C, # VERTICAL LINE
                 0b01111101: 0x007D, # RIGHT CURLY BRACKET
                 0b01111110: 0x2192, # RIGHTWARDS ARROW
                 0b01111111: 0x2190, # LEFTWARDS ARROW
                 0b10000000: 0x00C7, # LATIN CAPITAL LETTER C WITH CEDILLA
                 0b10000001: 0x00FC, # LATIN SMALL LETTER U WITH DIAERESIS
                 0b10000010: 0x00E9, # LATIN SMALL LETTER E WITH ACUTE
                 0b10000011: 0x00E2, # LATIN SMALL LETTER A WITH CIRCUMFLEX
                 0b10000100: 0x00E4, # LATIN SMALL LETTER A WITH DIAERESIS
                 0b10000101: 0x00E0, # LATIN SMALL LETTER A WITH GRAVE
                 0b10000110: 0x00E5, # LATIN SMALL LETTER A WITH RING ABOVE
                 0b10000111: 0x00E7, # LATIN SMALL LETTER C WITH CEDILLA
                 0b10001000: 0x00EA, # LATIN SMALL LETTER E WITH CIRCUMFLEX
                 0b10001001: 0x00EB, # LATIN SMALL LETTER E WITH DIAERESIS
                 0b10001010: 0x00E8, # LATIN SMALL LETTER E WITH GRAVE
                 0b10001011: 0x00EF, # LATIN SMALL LETTER I WITH DIAERESIS
                 0b10001100: 0x00EE, # LATIN SMALL LETTER I WITH CIRCUMFLEX
                 0b10001101: 0x00EC, # LATIN SMALL LETTER I WITH GRAVE
                 0b10001110: 0x00C4, # LATIN CAPITAL LETTER A WITH DIAERESIS
                 0b10001111: 0x00C5, # LATIN CAPITAL LETTER A WITH RING ABOVE
                 0b10010000: 0x00C9, # LATIN CAPITAL LETTER E WITH ACUTE
                 0b10010001: 0x00E6, # LATIN SMALL LETTER AE
                 0b10010010: 0x00C6, # LATIN CAPITAL LETTER AE
                 0b10010011: 0x00F4, # LATIN SMALL LETTER O WITH CIRCUMFLEX
                 0b10010100: 0x00F6, # LATIN SMALL LETTER O WITH DIAERESIS
                 0b10010101: 0x00F2, # LATIN SMALL LETTER O WITH GRAVE
                 0b10010110: 0x00FB, # LATIN SMALL LETTER U WITH CIRCUMFLEX
                 0b10010111: 0x00F9, # LATIN SMALL LETTER U WITH GRAVE
                 0b10011000: 0x00FF, # LATIN SMALL LETTER Y WITH DIAERESIS
                 0b10011001: 0x014E, # LATIN CAPITAL LETTER O WITH BREVE
                 0b10011010: 0x00DC, # LATIN CAPITAL LETTER U WITH DIAERESIS
                 0b10011011: 0x00F1, # LATIN SMALL LETTER N WITH TILDE
                 0b10011100: 0x00D1, # LATIN CAPITAL LETTER N WITH TILDE
                 0b10011101: 0x00AA, # FEMININE ORDINAL INDICATOR
                 0b10011110: 0x00BA, # MASCULINE ORDINAL INDICATOR
                 0b10011111: 0x00BF, # INVERTED QUESTION MARK
                 0b10100000: 0x00A0, # NO-BREAK SPACE
                 0b10100001: 0xFF61, # HALFWIDTH IDEOGRAPHIC FULL STOP
                 0b10100010: 0xFF62, # HALFWIDTH LEFT CORNER BRACKET
                 0b10100011: 0xFF63, # HALFWIDTH RIGHT CORNER BRACKET
                 0b10100100: 0xFF64, # HALFWIDTH IDEOGRAPHIC COMMA
                 0b10100101: 0xFF65, # HALFWIDTH KATAKANA MIDDLE DOT
                 0b10100110: 0xFF66, # HALFWIDTH KATAKANA LETTER WO
                 0b10100111: 0xFF67, # HALFWIDTH KATAKANA LETTER SMALL A
                 0b10101000: 0xFF68, # HALFWIDTH KATAKANA LETTER SMALL I
                 0b10101001: 0xFF69, # HALFWIDTH KATAKANA LETTER SMALL U
                 0b10101010: 0xFF6A, # HALFWIDTH KATAKANA LETTER SMALL E
                 0b10101011: 0xFF6B, # HALFWIDTH KATAKANA LETTER SMALL O
                 0b10101100: 0xFF6C, # HALFWIDTH KATAKANA LETTER SMALL YA
                 0b10101101: 0xFF6D, # HALFWIDTH KATAKANA LETTER SMALL YU
                 0b10101110: 0xFF6E, # HALFWIDTH KATAKANA LETTER SMALL YO
                 0b10101111: 0xFF6F, # HALFWIDTH KATAKANA LETTER SMALL TU
                 0b10110000: 0xFF70, # HALFWIDTH KATAKANA-HIRAGANA PROLONGED SOUND MARK
                 0b10110001: 0xFF71, # HALFWIDTH KATAKANA LETTER A
                 0b10110010: 0xFF72, # HALFWIDTH KATAKANA LETTER I
                 0b10110011: 0xFF73, # HALFWIDTH KATAKANA LETTER U
                 0b10110100: 0xFF74, # HALFWIDTH KATAKANA LETTER E
                 0b10110101: 0xFF75, # HALFWIDTH KATAKANA LETTER O
                 0b10110110: 0xFF76, # HALFWIDTH KATAKANA LETTER KA
                 0b10110111: 0xFF77, # HALFWIDTH KATAKANA LETTER KI
                 0b10111000: 0xFF78, # HALFWIDTH KATAKANA LETTER KU
                 0b10111001: 0xFF79, # HALFWIDTH KATAKANA LETTER KE
                 0b10111010: 0xFF7A, # HALFWIDTH KATAKANA LETTER KO
                 0b10111011: 0xFF7B, # HALFWIDTH KATAKANA LETTER SA
                 0b10111100: 0xFF7C, # HALFWIDTH KATAKANA LETTER SI
                 0b10111101: 0xFF7D, # HALFWIDTH KATAKANA LETTER SU
                 0b10111110: 0xFF7E, # HALFWIDTH KATAKANA LETTER SE
                 0b10111111: 0xFF7F, # HALFWIDTH KATAKANA LETTER SO
                 0b11000000: 0xFF80, # HALFWIDTH KATAKANA LETTER TA
                 0b11000001: 0xFF81, # HALFWIDTH KATAKANA LETTER TI
                 0b11000010: 0xFF82, # HALFWIDTH KATAKANA LETTER TU
                 0b11000011: 0xFF83, # HALFWIDTH KATAKANA LETTER TE
                 0b11000100: 0xFF84, # HALFWIDTH KATAKANA LETTER TO
                 0b11000101: 0xFF85, # HALFWIDTH KATAKANA LETTER NA
                 0b11000110: 0xFF86, # HALFWIDTH KATAKANA LETTER NI
                 0b11000111: 0xFF87, # HALFWIDTH KATAKANA LETTER NU
                 0b11001000: 0xFF88, # HALFWIDTH KATAKANA LETTER NE
                 0b11001001: 0xFF89, # HALFWIDTH KATAKANA LETTER NO
                 0b11001010: 0xFF8A, # HALFWIDTH KATAKANA LETTER HA
                 0b11001011: 0xFF8B, # HALFWIDTH KATAKANA LETTER HI
                 0b11001100: 0xFF8C, # HALFWIDTH KATAKANA LETTER HU
                 0b11001101: 0xFF8D, # HALFWIDTH KATAKANA LETTER HE
                 0b11001110: 0xFF8E, # HALFWIDTH KATAKANA LETTER HO
                 0b11001111: 0xFF8F, # HALFWIDTH KATAKANA LETTER MA
                 0b11010000: 0xFF90, # HALFWIDTH KATAKANA LETTER MI
                 0b11010001: 0xFF91, # HALFWIDTH KATAKANA LETTER MU
                 0b11010010: 0xFF92, # HALFWIDTH KATAKANA LETTER ME
                 0b11010011: 0xFF93, # HALFWIDTH KATAKANA LETTER MO
                 0b11010100: 0xFF94, # HALFWIDTH KATAKANA LETTER YA
                 0b11010101: 0xFF95, # HALFWIDTH KATAKANA LETTER YU
                 0b11010110: 0xFF96, # HALFWIDTH KATAKANA LETTER YO
                 0b11010111: 0xFF97, # HALFWIDTH KATAKANA LETTER RA
                 0b11011000: 0xFF98, # HALFWIDTH KATAKANA LETTER RI
                 0b11011001: 0xFF99, # HALFWIDTH KATAKANA LETTER RU
                 0b11011010: 0xFF9A, # HALFWIDTH KATAKANA LETTER RE
                 0b11011011: 0xFF9B, # HALFWIDTH KATAKANA LETTER RO
                 0b11011100: 0xFF9C, # HALFWIDTH KATAKANA LETTER WA
                 0b11011101: 0xFF9D, # HALFWIDTH KATAKANA LETTER N
                 0b11011110: 0xFF9E, # HALFWIDTH KATAKANA VOICED SOUND MARK
                 0b11011111: 0xFF9F, # HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK
                 0b11100000: 0x00E1, # LATIN SMALL LETTER A WITH ACUTE
                 0b11100001: 0x00ED, # LATIN SMALL LETTER I WITH ACUTE
                 0b11100010: 0x00F3, # LATIN SMALL LETTER O WITH ACUTE
                 0b11100011: 0x00FA, # LATIN SMALL LETTER U WITH ACUTE
                 0b11100100: 0x00A2, # CENT SIGN
                 0b11100101: 0x00A3, # POUND SIGN
                 0b11100110: 0x00A5, # YEN SIGN
                 0b11100111: 0x20A8, # RUPEE SIGN
                 0b11101000: 0x0192, # LATIN SMALL LETTER F WITH HOOK
                 0b11101001: 0x00A1, # INVERTED EXCLAMATION MARK
                 0b11101010: 0x00C3, # LATIN CAPITAL LETTER A WITH TILDE
                 0b11101011: 0x00E3, # LATIN SMALL LETTER A WITH TILDE
                 0b11101100: 0x00D5, # LATIN CAPITAL LETTER O WITH TILDE
                 0b11101101: 0x00F5, # LATIN SMALL LETTER O WITH TILDE
                 0b11101110: 0x00D8, # LATIN CAPITAL LETTER O WITH STROKE
                 0b11101111: 0x00F8, # LATIN SMALL LETTER O WITH STROKE
                 0b11110000: 0x02D9, # DOT ABOVE
                 0b11110001: 0x00A8, # DIAERESIS
                 0b11110010: 0x02DA, # RING ABOVE
                 0b11110011: 0x0060, # GRAVE ACCENT
                 0b11110100: 0x00B4, # ACUTE ACCENT
                 0b11110101: 0x00BD, # VULGAR FRACTION ONE HALF
                 0b11110110: 0x00BC, # VULGAR FRACTION ONE QUARTER
                 0b11110111: 0x00D7, # MULTIPLICATION SIGN
                 0b11111000: 0x00F7, # DIVISION SIGN
                 0b11111001: 0x2266, # LESS-THAN OVER EQUAL TO
                 0b11111010: 0x2267, # GREATER-THAN OVER EQUAL TO
                 0b11111011: 0x226A, # MUCH LESS-THAN
                 0b11111100: 0x226B, # MUCH GREATER-THAN
                 0b11111101: 0x2260, # NOT EQUAL TO
                 0b11111110: 0x221A, # SQUARE ROOT
                 0b11111111: 0x203E, # OVERLINE
               }



encoding_map = codecs.make_encoding_map(decoding_map)

# Add compatibility with existing code using user defined characters
encoding_map.update({ code: code for code in range(0, 7) })

class Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        return codecs.charmap_encode(input, errors, encoding_map)

    def decode(self, input, errors='strict'):
        return codecs.charmap_decode(input, errors, decoding_map)

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return codecs.charmap_encode(input,self.errors, encoding_map)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return codecs.charmap_decode(input,self.errors, decoding_map)[0]

class StreamWriter(Codec, codecs.StreamWriter):
    pass

class StreamReader(Codec, codecs.StreamReader):
    pass

def find_st7036(encoding):
    if encoding.lower() != 'st7036':
        return None
    return codecs.CodecInfo(name='st7036',
                            encode=Codec().encode,
                            decode=Codec().decode,
                            incrementalencoder=IncrementalEncoder,
                            incrementaldecoder=IncrementalDecoder,
                            streamreader=StreamReader,
                            streamwriter=StreamWriter,
                           )

codecs.register(find_st7036)

if __name__ == '__main__':
    import sys
    print("Diode électro-luminescentes".encode('st7036'))
    print(b'Diode \x82lectro-luminescentes'.decode('st7036'))
