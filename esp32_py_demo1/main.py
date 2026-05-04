from machine import SoftI2C, Pin, SPI
import time

# ===== DISPLAY INITIALIZATION =====
print("Initializing...")

i2c = SoftI2C(sda=Pin(15), scl=Pin(14), freq=400000)

# Configure TCA9554
i2c.writeto(0x20, bytes([0x03, 0x00]))
i2c.writeto(0x20, bytes([0x01, 0x02]))
time.sleep_ms(50)
i2c.writeto(0x20, bytes([0x01, 0x07]))
time.sleep_ms(150)

# Initialize display
import amoled
spi = SPI(2, baudrate=80_000_000, sck=Pin(11), mosi=None, miso=None)
panel = amoled.QSPIPanel(
    spi=spi,
    data=(Pin(4), Pin(5), Pin(6), Pin(7)),
    dc=Pin(5), cs=Pin(12),
    pclk=80_000_000, width=368, height=448
)
display = amoled.AMOLED(panel, type=2, bpp=16, auto_refresh=True)
display.init()
display.brightness(255)

# ===== BOOT BUTTON =====
boot_button = Pin(0, Pin.IN, Pin.PULL_UP)  # BOOT button on GPIO 0
boot_button_pressed = False
boot_button_start_time = 0

# ===== FIXED COLOR FUNCTION =====
def make_color(r, g, b):
    c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | ((b & 0xF8) >> 3)
    return ((c >> 8) & 0x00FF) | ((c << 8) & 0xFF00)

GREEN = make_color(0, 95, 0)
BLACK = 0x0000
GREY = make_color(50, 50, 50)
DARK_GREY = make_color(30, 30, 30)
GAMEOVER_BTN = make_color(0, 95, 0)
WHITE = 0xFFFF

# ===== SEVEN SEGMENT FONT (for time) =====
SEVEN_SEG_FONT = {
    '0': [0b01110, 0b10001, 0b10001, 0b00000, 0b10001, 0b10001, 0b01110],
    '1': [0b00001, 0b00001, 0b00001, 0b00000, 0b00001, 0b00001, 0b00001],
    '2': [0b01110, 0b00001, 0b00001, 0b01110, 0b10000, 0b10000, 0b01110],
    '3': [0b01110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b01110],
    '4': [0b10001, 0b10001, 0b10001, 0b01110, 0b00001, 0b00001, 0b00001],
    '5': [0b01110, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b01110],
    '6': [0b01110, 0b10000, 0b10000, 0b01110, 0b10001, 0b10001, 0b01110],
    '7': [0b01110, 0b00001, 0b00001, 0b00000, 0b00001, 0b00001, 0b00001],
    '8': [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
    '9': [0b01110, 0b10001, 0b10001, 0b01110, 0b00001, 0b00001, 0b01110],
    ':': [0b00000, 0b00100, 0b00000, 0b00000, 0b00000, 0b00100, 0b00000],
}

# ===== CODE FONT (for date and text) =====
CODE_FONT = {
    '0': [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    '1': [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    '2': [0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111],
    '3': [0b01110, 0b10001, 0b00001, 0b00110, 0b00001, 0b10001, 0b01110],
    '4': [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
    '5': [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
    '6': [0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
    '7': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
    '8': [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
    '9': [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100],
    '-': [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
    ':': [0b00000, 0b00100, 0b00100, 0b00000, 0b00100, 0b00100, 0b00000],
    ' ': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    'A': [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    'B': [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
    'C': [0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
    'D': [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
    'E': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
    'F': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
    'G': [0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01110],
    'H': [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    'I': [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    'J': [0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100],
    'K': [0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
    'L': [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
    'M': [0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
    'N': [0b10001, 0b11001, 0b10101, 0b10101, 0b10011, 0b10001, 0b10001],
    'O': [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'P': [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
    'Q': [0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
    'R': [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
    'S': [0b01110, 0b10001, 0b10000, 0b01110, 0b00001, 0b10001, 0b01110],
    'T': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    'U': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'V': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    'W': [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010],
    'X': [0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
    'Y': [0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
    'Z': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
    '%': [0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011],
    '.': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100],
    ',': [0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00100, 0b01000],
    '!': [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
    '?': [0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0b00000, 0b00100],
    "'": [0b00100, 0b00100, 0b01000, 0b00000, 0b00000, 0b00000, 0b00000],
    '"': [0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '/': [0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000],
    '*': [0b00000, 0b00100, 0b10101, 0b01110, 0b10101, 0b00100, 0b00000],
    '+': [0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000],
    '-': [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
    '=': [0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000],
    '(': [0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010],
    ')': [0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000],
    'x': [0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
}

# ===== BOOK FONT (lowercase for reading) =====
BOOK_FONT = {
    ' ': [0,0,0,0,0,0,0],
    '.': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100],
    ',': [0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00100, 0b01000],
    '!': [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
    '?': [0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0b00000, 0b00100],
    "'": [0b00100, 0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000],
    ''': [0b00100, 0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000],  # Right single curly quote
    ''': [0b00100, 0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000],  # Left single curly quote
    '`': [0b00100, 0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000],  # Grave accent (backtick)
    'Â´': [0b00100, 0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000],  # Acute accent
    '"': [0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '"': [0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],  # Left double curly quote
    '"': [0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],  # Right double curly quote
    'â€”': [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],  # Em-dash
    'â€“': [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],  # En-dash
    '-': [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
    ':': [0b00000, 0b00100, 0b00100, 0b00000, 0b00100, 0b00100, 0b00000],
    ';': [0b00000, 0b00100, 0b00100, 0b00000, 0b00100, 0b00100, 0b01000],
    '/': [0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000],
    '0': [0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
    '1': [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    '2': [0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111],
    '3': [0b01110, 0b10001, 0b00001, 0b00110, 0b00001, 0b10001, 0b01110],
    '4': [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
    '5': [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
    '6': [0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
    '7': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
    '8': [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
    '9': [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100],
    'A': [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    'B': [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
    'C': [0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
    'D': [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
    'E': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
    'F': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
    'G': [0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01110],
    'H': [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    'I': [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    'J': [0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100],
    'K': [0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
    'L': [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
    'M': [0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
    'N': [0b10001, 0b11001, 0b10101, 0b10101, 0b10011, 0b10001, 0b10001],
    'O': [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'P': [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
    'Q': [0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
    'R': [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
    'S': [0b01110, 0b10001, 0b10000, 0b01110, 0b00001, 0b10001, 0b01110],
    'T': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    'U': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'V': [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    'W': [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010],
    'X': [0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
    'Y': [0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
    'Z': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
    'a': [0b00000, 0b00000, 0b01110, 0b00001, 0b01111, 0b10001, 0b01111],
    'b': [0b10000, 0b10000, 0b10110, 0b11001, 0b10001, 0b10001, 0b11110],
    'c': [0b00000, 0b00000, 0b01110, 0b10000, 0b10000, 0b10001, 0b01110],
    'd': [0b00001, 0b00001, 0b01101, 0b10011, 0b10001, 0b10001, 0b01111],
    'e': [0b00000, 0b00000, 0b01110, 0b10001, 0b11111, 0b10000, 0b01110],
    'f': [0b00110, 0b01001, 0b01000, 0b11100, 0b01000, 0b01000, 0b01000],
    'g': [0b00000, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110],
    'h': [0b10000, 0b10000, 0b10110, 0b11001, 0b10001, 0b10001, 0b10001],
    'i': [0b00100, 0b00000, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110],
    'j': [0b00010, 0b00000, 0b00110, 0b00010, 0b00010, 0b10010, 0b01100],
    'k': [0b10000, 0b10000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010],
    'l': [0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    'm': [0b00000, 0b00000, 0b11010, 0b10101, 0b10101, 0b10001, 0b10001],
    'n': [0b00000, 0b00000, 0b10110, 0b11001, 0b10001, 0b10001, 0b10001],
    'o': [0b00000, 0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110],
    'p': [0b00000, 0b00000, 0b11110, 0b10001, 0b11110, 0b10000, 0b10000],
    'q': [0b00000, 0b00000, 0b01101, 0b10011, 0b01111, 0b00001, 0b00001],
    'r': [0b00000, 0b00000, 0b10110, 0b11001, 0b10000, 0b10000, 0b10000],
    's': [0b00000, 0b00000, 0b01110, 0b10000, 0b01110, 0b00001, 0b11110],
    't': [0b01000, 0b01000, 0b11100, 0b01000, 0b01000, 0b01001, 0b00110],
    'u': [0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b10011, 0b01101],
    'v': [0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    'w': [0b00000, 0b00000, 0b10001, 0b10001, 0b10101, 0b10101, 0b01010],
    'x': [0b00000, 0b00000, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001],
    'y': [0b00000, 0b00000, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110],
    'z': [0b00000, 0b00000, 0b11111, 0b00010, 0b00100, 0b01000, 0b11111],
}

def draw_char(display, char, x, y, color, scale, font):
    if char not in font:
        # Map unknown chars to reasonable fallbacks
        fc = None
        if char in '\u201c\u201d\u201e\u00ab\u00bb':
            fc = '"'  # Curly/fancy double quotes → straight double quote
        elif char in '\u2018\u2019\u201a\u201b\u0060\u00b4':
            fc = "'"  # Curly/fancy single quotes → apostrophe
        elif char in '\u2013\u2014\u2012':
            fc = '-'  # En/em dash → hyphen
        if fc and fc in font:
            rows = font[fc]
            for row_idx, row in enumerate(rows):
                for col in range(5):
                    if row & (0b10000 >> col):
                        display.fill_rect(x + col * scale, y + row_idx * scale, scale, scale, color)
        return 6 * scale
    rows = font[char]
    for row_idx, row in enumerate(rows):
        for col in range(5):
            if row & (0b10000 >> col):
                display.fill_rect(x + col * scale, y + row_idx * scale, scale, scale, color)
    return 6 * scale

def draw_text(display, text, x, y, color, scale, font):
    cx = x
    for char in text:
        cx += draw_char(display, char, cx, y, color, scale, font)

# ===== RTC FUNCTIONS =====
def read_rtc():
    try:
        i2c.writeto(0x51, bytes([0x04]))
        data = i2c.readfrom(0x51, 3)
        seconds = (data[0] & 0x7F)
        seconds = (seconds >> 4) * 10 + (seconds & 0x0F)
        minutes = (data[1] & 0x7F)
        minutes = (minutes >> 4) * 10 + (minutes & 0x0F)
        hours = (data[2] & 0x3F)
        hours = (hours >> 4) * 10 + (hours & 0x0F)
        return (hours, minutes, seconds)
    except:
        return (12, 0, 0)

def read_date_rtc():
    try:
        i2c.writeto(0x51, bytes([0x07]))
        data = i2c.readfrom(0x51, 4)
        day = data[0] & 0x3F
        day = (day >> 4) * 10 + (day & 0x0F)
        month = data[2] & 0x1F
        month = (month >> 4) * 10 + (month & 0x0F)
        year = data[3]
        year = (year >> 4) * 10 + (year & 0x0F)
        year = 2000 + year
        return (year, month, day)
    except:
        return (2026, 1, 23)

def write_rtc(hours, minutes):
    try:
        sec_bcd = 0
        min_bcd = ((minutes // 10) << 4) | (minutes % 10)
        hr_bcd = ((hours // 10) << 4) | (hours % 10)
        i2c.writeto_mem(0x51, 0x04, bytes([sec_bcd, min_bcd, hr_bcd]))
    except:
        pass

def write_date_rtc(year, month, day):
    try:
        yr = year - 2000
        day_bcd = ((day // 10) << 4) | (day % 10)
        mon_bcd = ((month // 10) << 4) | (month % 10)
        yr_bcd = ((yr // 10) << 4) | (yr % 10)
        i2c.writeto_mem(0x51, 0x07, bytes([day_bcd, 0, mon_bcd, yr_bcd]))
    except:
        pass

# ===== BATTERY FUNCTIONS =====
def read_battery_percent():
    try:
        data = i2c.readfrom_mem(0x34, 0xA4, 1)
        return data[0]
    except:
        return 0

def read_battery_charging():
    try:
        data = i2c.readfrom_mem(0x34, 0x01, 1)
        return (data[0] & 0x20) != 0
    except:
        return False

def read_battery_voltage():
    """Read battery voltage in mV from AXP2101"""
    try:
        data = i2c.readfrom_mem(0x34, 0x34, 2)
        # 14-bit value, 1mV per step
        mv = ((data[0] & 0x3F) << 8) | data[1]
        return mv
    except:
        return 0

def voltage_to_percent(mv):
    """Convert battery voltage to percentage with decimal precision using LiPo curve"""
    if mv >= 4150:
        return 100.0
    elif mv >= 4000:
        return 90.0 + (mv - 4000) * 10.0 / 150.0
    elif mv >= 3850:
        return 70.0 + (mv - 3850) * 20.0 / 150.0
    elif mv >= 3700:
        return 40.0 + (mv - 3700) * 30.0 / 150.0
    elif mv >= 3550:
        return 15.0 + (mv - 3550) * 25.0 / 150.0
    elif mv >= 3400:
        return 5.0 + (mv - 3400) * 10.0 / 150.0
    elif mv >= 3200:
        return (mv - 3200) * 5.0 / 200.0
    else:
        return 0.0

battery_time_remaining = 0  # Estimated minutes remaining

def update_battery_time_estimate():
    """Battery time estimation for discharge and charge"""
    global battery_time_remaining

    percent = read_battery_percent()
    charging = read_battery_charging()

    if charging:
        if percent >= 100:
            battery_time_remaining = -2  # Fully charged
        else:
            # 240mAh @ 300mA charge = ~60 min total, 0.6 min per %
            battery_time_remaining = -100 - int((100 - percent) * 0.6)
    elif percent == 0:
        battery_time_remaining = 0
    else:
        # Simple linear estimate: 1% = 2.25 minutes (225 min total / 100%)
        battery_time_remaining = int(percent * 2.25)

def draw_battery_icon(x, y, percent):
    w, h = 40, 20
    display.rect(x, y, w, h, GREY)
    display.rect(x + 1, y + 1, w - 2, h - 2, GREY)
    display.fill_rect(x + w, y + 5, 5, 10, GREY)
    fill_w = int((w - 8) * percent / 100)
    if fill_w > 0:
        display.fill_rect(x + 4, y + 4, fill_w, h - 8, GREY)

# ===== TOUCH FUNCTIONS =====
def read_touch():
    try:
        i2c.writeto(0x38, bytes([0x02]))
        data = i2c.readfrom(0x38, 5)
        num_points = data[0] & 0x0F
        if num_points > 0:
            x = ((data[1] & 0x0F) << 8) | data[2]
            y = ((data[3] & 0x0F) << 8) | data[4]
            return (x, y)
        return None
    except:
        return None

# ===== IMU FUNCTIONS =====
def init_imu():
    try:
        i2c.writeto(0x6B, bytes([0x00]))
        whoami = i2c.readfrom(0x6B, 1)
        print(f"IMU WHO_AM_I: {hex(whoami[0])}")
        i2c.writeto_mem(0x6B, 0x60, bytes([0xB0]))
        time.sleep_ms(30)
        time.sleep_ms(30)
        i2c.writeto_mem(0x6B, 0x02, bytes([0x60]))
        i2c.writeto_mem(0x6B, 0x03, bytes([0x25]))
        i2c.writeto_mem(0x6B, 0x06, bytes([0x00]))
        i2c.writeto_mem(0x6B, 0x08, bytes([0x01]))
        time.sleep_ms(50)
        ax, ay, az = read_accel_raw()
        print(f"IMU test read: x={ax}, y={ay}, z={az}")
        print("IMU initialized!")
        return True
    except Exception as e:
        print(f"IMU init failed: {e}")
        return False

def read_accel_raw():
    try:
        data = i2c.readfrom_mem(0x6B, 0x35, 6)
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
        if x > 32767: x -= 65536
        if y > 32767: y -= 65536
        if z > 32767: z -= 65536
        return (x, y, z)
    except:
        return (0, 0, 0)

def read_accel():
    try:
        data = i2c.readfrom_mem(0x6B, 0x35, 6)
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
        if x > 32767: x -= 65536
        if y > 32767: y -= 65536
        if z > 32767: z -= 65536
        return (x / 4096, y / 4096, z / 4096)
    except:
        return (0, 0, 1)

print("Initializing IMU...")
init_imu()

# ===== SD CARD FUNCTIONS =====
sd_card = None
sd_spi = None

class EXIO7_CS:
    def __init__(self, i2c):
        self.i2c = i2c
        self.state = 0x87
    def __call__(self, val):
        if val:
            self.state |= 0x80
        else:
            self.state &= ~0x80
        self.i2c.writeto(0x20, bytes([0x01, self.state]))
        time.sleep_us(10)
    def init(self, mode, value=1):
        self(value)

def init_sd_card():
    global sd_card, sd_spi
    try:
        # Set EXIO7 high (CS inactive)
        i2c.writeto(0x20, bytes([0x01, 0x87]))
        time.sleep_ms(100)

        cs = EXIO7_CS(i2c)
        sd_spi = SPI(1, baudrate=100000, polarity=0, phase=0,
                     sck=Pin(2), mosi=Pin(1), miso=Pin(3))

        # Send init clocks
        cs(1)
        time.sleep_ms(100)
        for _ in range(10):
            sd_spi.write(b'\xff' * 8)

        # CMD0
        cs(0)
        sd_spi.write(bytes([0x40, 0, 0, 0, 0, 0x95]))
        r = 0xFF
        for _ in range(100):
            r = sd_spi.read(1, 0xFF)[0]
            if not (r & 0x80):
                break
        cs(1)
        sd_spi.write(b'\xff')
        if r != 0x01:
            print("SD: No card")
            return False

        # CMD8
        cs(0)
        sd_spi.write(bytes([0x48, 0, 0, 0x01, 0xAA, 0x87]))
        for _ in range(100):
            r = sd_spi.read(1, 0xFF)[0]
            if not (r & 0x80):
                break
        sd_spi.read(4, 0xFF)
        cs(1)
        sd_spi.write(b'\xff')

        # ACMD41
        for attempt in range(100):
            cs(0)
            sd_spi.write(bytes([0x77, 0, 0, 0, 0, 0x65]))
            for _ in range(100):
                r = sd_spi.read(1, 0xFF)[0]
                if not (r & 0x80):
                    break
            cs(1)
            sd_spi.write(b'\xff')

            cs(0)
            sd_spi.write(bytes([0x69, 0x40, 0, 0, 0, 0x77]))
            for _ in range(100):
                r = sd_spi.read(1, 0xFF)[0]
                if not (r & 0x80):
                    break
            cs(1)
            sd_spi.write(b'\xff')

            if r == 0:
                break
            time.sleep_ms(50)

        if r != 0:
            print("SD: Init failed")
            return False

        # Create SD object
        class SimpleSD:
            def __init__(self, spi, cs):
                self.spi = spi
                self.cs = cs
            def _read_single(self, block, buf):
                self.cs(0)
                time.sleep_us(10)
                cmd = bytearray(6)
                cmd[0] = 0x51
                cmd[1] = (block >> 24) & 0xFF
                cmd[2] = (block >> 16) & 0xFF
                cmd[3] = (block >> 8) & 0xFF
                cmd[4] = block & 0xFF
                cmd[5] = 0xFF
                self.spi.write(cmd)
                r = 0xFF
                for _ in range(100):
                    r = self.spi.read(1, 0xFF)[0]
                    if not (r & 0x80):
                        break
                if r != 0:
                    self.cs(1)
                    self.spi.write(b'\xff')
                    raise OSError(5)
                t = 0xFF
                for _ in range(2000):
                    t = self.spi.read(1, 0xFF)[0]
                    if t == 0xFE:
                        break
                if t != 0xFE:
                    self.cs(1)
                    self.spi.write(b'\xff')
                    raise OSError(5)
                self.spi.readinto(buf, 0xFF)
                self.spi.read(2, 0xFF)
                self.cs(1)
                self.spi.write(b'\xff')
            def readblocks(self, block, buf):
                nblocks = len(buf) // 512
                if nblocks == 1:
                    self._read_single(block, buf)
                else:
                    mv = memoryview(buf)
                    for i in range(nblocks):
                        self._read_single(block + i, mv[i*512:(i+1)*512])
            def writeblocks(self, block, buf):
                pass  # Read-only for now
            def ioctl(self, op, arg):
                if op == 4:
                    return 1000000
                if op == 5:
                    return 512

        sd_card = SimpleSD(sd_spi, cs)
        print("SD: OK")
        return True
    except Exception as e:
        print(f"SD: Error {e}")
        return False


# ===== ADDITIONAL IMPORTS =====
import os
import gc
import math

# ===== APP USAGE TRACKING =====
app_usage = {}  # Dict of app_name: seconds spent
app_enter_time = 0  # When current app was entered

def load_usage():
    global app_usage
    try:
        with open('usage.txt', 'r') as f:
            for line in f:
                if ':' in line:
                    name, secs = line.strip().split(':')
                    app_usage[name] = int(secs)
    except:
        app_usage = {}
    # Migrate old "brick" entry to "BRICK BREAKER"
    if "brick" in app_usage:
        old = app_usage.pop("brick")
        if "BRICK BREAKER" in app_usage:
            app_usage["BRICK BREAKER"] += old
        else:
            app_usage["BRICK BREAKER"] = old
        save_usage()

def save_usage():
    try:
        with open('usage.txt', 'w') as f:
            for name, secs in app_usage.items():
                f.write(f"{name}:{secs}\n")
    except:
        pass

def track_app_enter():
    global app_enter_time
    app_enter_time = time.ticks_ms()

def track_app_exit(app_name):
    global app_usage
    if app_enter_time > 0:
        elapsed = time.ticks_diff(time.ticks_ms(), app_enter_time) // 1000  # seconds
        if app_name in app_usage:
            app_usage[app_name] += elapsed
        else:
            app_usage[app_name] = elapsed
        save_usage()

load_usage()

# ===== SAFE MODE =====
safe_mode = False
SAFE_HIDDEN = [0, 1, 3, 10, 11, 12, 14, 15, 16, 17, 19, 20, 22, 23, 26]

# ===== DOCS MODE =====
docs_mode = False
DOCS_HIDDEN = [2, 18, 19]  # BOOKS, NOTES, PHOTOS

def get_visible_apps():
    hidden = set()
    if safe_mode:
        hidden.update(SAFE_HIDDEN)
    if not docs_mode:
        hidden.update(DOCS_HIDDEN)
    if hidden:
        return [i for i in range(len(APPS)) if i not in hidden]
    return list(range(len(APPS)))

def load_safe_mode():
    global safe_mode
    try:
        with open('safe_mode.txt', 'r') as f:
            safe_mode = f.read().strip() == '1'
    except:
        safe_mode = False

def save_safe_mode():
    try:
        with open('safe_mode.txt', 'w') as f:
            f.write('1' if safe_mode else '0')
    except:
        pass

def load_docs_mode():
    global docs_mode
    try:
        with open('docs_mode.txt', 'r') as f:
            docs_mode = f.read().strip() == '1'
    except:
        docs_mode = False

def save_docs_mode():
    try:
        with open('docs_mode.txt', 'w') as f:
            f.write('1' if docs_mode else '0')
    except:
        pass

# ===== GLOBE ANIMATION =====
globe_animated = False
globe_frame = 0
globe_last_frame_ms = 0
GLOBE_FRAMES = 110

def load_globe_setting():
    global globe_animated
    try:
        with open('globe.txt', 'r') as f:
            globe_animated = f.read().strip() == '1'
    except:
        globe_animated = False

def save_globe_setting():
    try:
        with open('globe.txt', 'w') as f:
            f.write('1' if globe_animated else '0')
    except:
        pass

def draw_app_sort_settings():
    display.fill(BLACK)
    draw_text(display, "APP SORT", 100, 15, GREY, 3, CODE_FONT)
    bw = 150
    bh = 70
    lx = 25
    rx = 193
    by = 180
    # ALL button (alphabetical)
    display.fill_rect(lx, by, bw, bh, GREEN if app_sort_mode == 0 else DARK_GREY)
    t = "ALL"
    tw = len(t) * 18
    draw_text(display, t, lx + (bw - tw) // 2, by + 23, WHITE if app_sort_mode == 0 else GREY, 3, CODE_FONT)
    # CATEGORY button
    display.fill_rect(rx, by, bw, bh, GREEN if app_sort_mode == 1 else DARK_GREY)
    t = "CATEGORY"
    tw = len(t) * 18
    draw_text(display, t, rx + (bw - tw) // 2, by + 23, WHITE if app_sort_mode == 1 else GREY, 3, CODE_FONT)

def draw_globe_settings():
    display.fill(BLACK)
    draw_text(display, "GLOBE", 130, 15, GREY, 3, CODE_FONT)
    # Two buttons side by side
    bw = 150
    bh = 70
    lx = 25
    rx = 193
    by = 180
    # STATIC button
    display.fill_rect(lx, by, bw, bh, GREEN if not globe_animated else DARK_GREY)
    t = "STATIC"
    tw = len(t) * 18
    draw_text(display, t, lx + (bw - tw) // 2, by + 23, WHITE if not globe_animated else GREY, 3, CODE_FONT)
    # ANIMATED button
    display.fill_rect(rx, by, bw, bh, GREEN if globe_animated else DARK_GREY)
    t = "ANIMATED"
    tw = len(t) * 18
    draw_text(display, t, rx + (bw - tw) // 2, by + 23, WHITE if globe_animated else GREY, 3, CODE_FONT)

def draw_globe_screen():
    global globe_frame, globe_last_frame_ms
    display.fill(BLACK)
    if globe_animated:
        globe_frame = 0
        globe_last_frame_ms = time.ticks_ms()
        display.jpg('globe/GLOBE_001.jpg', 68, 175)
    else:
        display.jpg("GLOBE_1.jpg", 68, 175)
    hours, minutes, seconds = read_rtc()
    year, month, day = read_date_rtc()
    time_text = f"{hours:02d}:{minutes:02d}"
    date_text = f"{year}-{month:02d}-{day:02d}"
    scale = 7
    text_width = len(time_text) * 6 * scale
    center_x = (368 - text_width) // 2
    draw_text(display, time_text, center_x, 50, GREY, scale, SEVEN_SEG_FONT)
    scale_date = 4
    date_width = len(date_text) * 6 * scale_date
    center_x_date = (368 - date_width) // 2
    draw_text(display, date_text, center_x_date, 120, GREY, scale_date, CODE_FONT)
    # Show step count if enabled
    if steps_enabled:
        steps_text = f"{step_count} STEPS"
        steps_width = len(steps_text) * 6 * 2
        center_x_steps = (368 - steps_width) // 2
        draw_text(display, steps_text, center_x_steps, 420, GREEN, 2, CODE_FONT)

APPS = ["2048", "BATTLESHIP", "BOOKS", "BRICK BREAKER", "CALCULATOR", "CHECKERS", "CHESS", "CLOCK", "CONNECT FOUR", "DRAW", "FLAPPY BIRD", "GAME OF LIFE", "GEOMETRY DASH", "GYRO LEVEL", "LASER", "MASTERMIND", "MAZE", "MINESWEEPER", "NOTES", "PHOTOS", "PONG", "SLIDING PUZZLE", "SNAKE", "SPACE INVADERS", "SUDOKU", "TIC-TAC-TOE", "UNFAIR FLIPS", "WORD SEARCH", "WORDLE", "SETTINGS"]

# Category indices (into APPS list)
# 0=2048,1=BATTLESHIP,2=BOOKS,3=BRICK,4=CALC,5=CHECKERS,6=CHESS,7=CLOCK,
# 8=CONNECT4,9=DRAW,10=FLAPPY,11=LIFE,12=GDASH,13=GYRO,14=LASER,
# 15=MASTERMIND,16=MAZE,17=MINESWEEPER,18=NOTES,19=PHOTOS,20=PONG,
# 21=SLIDING,22=SNAKE,23=INVADERS,24=SUDOKU,25=TICTACTOE,26=FLIPS,
# 27=WORDSEARCH,28=WORDLE,29=SETTINGS
CAT_SINGLE = [0, 3, 10, 11, 12, 15, 16, 17, 21, 22, 23, 24, 26, 27]
CAT_MULTI = [1, 5, 6, 8, 20, 25, 28]
CAT_TOOLS = [4, 7, 29]
CAT_UTIL = [2, 9, 13, 14, 18, 19]
CAT_NAMES = ["SINGLEPLAYER", "MULTIPLAYER", "TOOLS", "UTILITY"]
CAT_LISTS = [CAT_SINGLE, CAT_MULTI, CAT_TOOLS, CAT_UTIL]

# App sort mode: 0=alphabetical, 1=categories
app_sort_mode = 0
menu_category = -1  # -1=show category buttons, 0-3=show filtered list

def load_app_sort():
    global app_sort_mode
    try:
        with open('app_sort.txt', 'r') as f:
            app_sort_mode = int(f.read().strip())
    except:
        app_sort_mode = 0

def save_app_sort():
    try:
        with open('app_sort.txt', 'w') as f:
            f.write(str(app_sort_mode))
    except:
        pass

def draw_menu_screen():
    global app_scroll
    display.fill(BLACK)
    hours, minutes, seconds = read_rtc()
    time_text = f"{hours:02d}:{minutes:02d}"
    draw_text(display, time_text, 15, 15, GREY, 3, CODE_FONT)
    percent = read_battery_percent()
    draw_battery_icon(308, 12, percent)
    # Show category name if in category mode
    if app_sort_mode == 1 and menu_category >= 0:
        cn = CAT_NAMES[menu_category]
        cw = len(cn) * 12
        draw_text(display, cn, (368 - cw) // 2, 50, GREEN, 2, CODE_FONT)
    y_start = 80
    row_height = 50
    max_visible = 7  # How many apps fit on screen
    if app_sort_mode == 1 and menu_category >= 0:
        vis = get_category_apps(menu_category)
    else:
        vis = get_visible_apps()
    if app_scroll > max(0, len(vis) - max_visible):
        app_scroll = max(0, len(vis) - max_visible)
    # Draw scroll up indicator if not at top
    if app_scroll > 0:
        cx = 184
        for i in range(10):
            display.fill_rect(cx - i, 62 + 10 - i, i * 2 + 1, 2, GREY)
    # Draw visible apps
    for idx in range(max_visible):
        vi = app_scroll + idx
        if vi >= len(vis):
            break
        y = y_start + idx * row_height
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, APPS[vis[vi]], 30, y + 15, GREY, 3, CODE_FONT)
    # Final divider
    visible_count = min(max_visible, len(vis) - app_scroll)
    y_final = y_start + visible_count * row_height
    display.fill_rect(20, y_final, 328, 3, DARK_GREY)
    # Draw scroll down indicator if more apps below
    if app_scroll + max_visible < len(vis):
        cx = 184
        for i in range(10):
            display.fill_rect(cx - i, y_final + 6 + i, i * 2 + 1, 2, GREY)

def draw_category_screen():
    """Draw the 4 category buttons filling the screen."""
    display.fill(BLACK)
    hours, minutes, seconds = read_rtc()
    time_text = f"{hours:02d}:{minutes:02d}"
    draw_text(display, time_text, 15, 15, GREY, 3, CODE_FONT)
    percent = read_battery_percent()
    draw_battery_icon(308, 12, percent)
    # 4 buttons: 2x2 grid filling below header
    gap = 8
    bw = (368 - gap * 3) // 2  # ~172px wide
    bh = (448 - 55 - gap * 3) // 2  # ~188px tall
    x1 = gap
    x2 = gap * 2 + bw
    y1 = 55
    y2 = 55 + bh + gap
    # Draw buttons
    display.fill_rect(x1, y1, bw, bh, GREEN)
    display.fill_rect(x2, y1, bw, bh, GREEN)
    display.fill_rect(x1, y2, bw, bh, GREEN)
    display.fill_rect(x2, y2, bw, bh, GREEN)
    # SINGLE PLAYER
    t = "SINGLE"
    tw = len(t) * 18
    draw_text(display, t, x1 + (bw - tw) // 2, y1 + bh // 2 - 24, WHITE, 3, CODE_FONT)
    t = "PLAYER"
    tw = len(t) * 18
    draw_text(display, t, x1 + (bw - tw) // 2, y1 + bh // 2 + 4, GREY, 3, CODE_FONT)
    # MULTI PLAYER
    t = "MULTI"
    tw = len(t) * 18
    draw_text(display, t, x2 + (bw - tw) // 2, y1 + bh // 2 - 24, WHITE, 3, CODE_FONT)
    t = "PLAYER"
    tw = len(t) * 18
    draw_text(display, t, x2 + (bw - tw) // 2, y1 + bh // 2 + 4, GREY, 3, CODE_FONT)
    # TOOLS
    t = "TOOLS"
    tw = len(t) * 18
    draw_text(display, t, x1 + (bw - tw) // 2, y2 + (bh - 18) // 2, WHITE, 3, CODE_FONT)
    # UTILITY
    t = "UTILITY"
    tw = len(t) * 18
    draw_text(display, t, x2 + (bw - tw) // 2, y2 + (bh - 18) // 2, WHITE, 3, CODE_FONT)

def get_category_apps(cat_idx):
    """Get visible apps filtered by category."""
    cat_list = CAT_LISTS[cat_idx]
    hidden = set()
    if safe_mode:
        hidden.update(SAFE_HIDDEN)
    if not docs_mode:
        hidden.update(DOCS_HIDDEN)
    return [i for i in cat_list if i not in hidden]

SETTINGS_ITEMS = ["BATTERY", "BRIGHTNESS", "VOLUME", "PEDOMETER", "GLOBE", "APP SORT", "STATS", "TIME", "ABOUT"]
brightness_level = 100
volume_level = 0

# Time settings temp vars
time_set_h = 0
time_set_m = 0
time_set_y = 2026
time_set_mo = 1
time_set_d = 1

# Step counter settings
steps_enabled = False
step_count = 0
step_last_mag = 1.0  # Last acceleration magnitude
step_last_time = 0   # Last step timestamp for debounce
step_threshold = 1.15  # Acceleration magnitude threshold for step detection
step_debounce = 300    # Minimum ms between steps

def get_settings_items():
    if safe_mode:
        return [s for s in SETTINGS_ITEMS if s != "STATS"]
    return SETTINGS_ITEMS

SETTINGS_VISIBLE = 7

def draw_settings_app():
    display.fill(BLACK)
    draw_text(display, "SETTINGS", 120, 15, GREY, 3, CODE_FONT)
    y_start = 80
    row_height = 50
    items = get_settings_items()
    if settings_scroll > max(0, len(items) - SETTINGS_VISIBLE):
        settings_scroll_fix = max(0, len(items) - SETTINGS_VISIBLE)
    for i in range(SETTINGS_VISIBLE):
        vi = settings_scroll + i
        if vi >= len(items):
            break
        y = y_start + i * row_height
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, items[vi], 30, y + 15, GREY, 3, CODE_FONT)
    y_final = y_start + min(SETTINGS_VISIBLE, len(items) - settings_scroll) * row_height
    display.fill_rect(20, y_final, 328, 3, DARK_GREY)
    # Scroll arrows
    cx = 184
    if settings_scroll > 0:
        for i in range(10):
            display.fill_rect(cx - i, 55 + i, i * 2 + 1, 2, GREY)
    if settings_scroll + SETTINGS_VISIBLE < len(items):
        for i in range(10):
            display.fill_rect(cx - i, 430 + 10 - i, i * 2 + 1, 2, GREY)

battery_last_percent = -1
battery_last_voltage = -1
battery_last_charging = None
battery_last_time_remaining = -999

def draw_battery_settings():
    global battery_last_percent, battery_last_voltage, battery_last_charging, battery_last_time_remaining
    battery_last_percent = -1  # Force full redraw
    battery_last_voltage = -1
    battery_last_charging = None
    battery_last_time_remaining = -999
    display.fill(BLACK)
    draw_text(display, "BATTERY", 130, 15, GREY, 3, CODE_FONT)

    y_start = 80
    row_height = 45
    display.fill_rect(20, y_start, 328, 3, DARK_GREY)
    display.fill_rect(20, y_start + row_height, 328, 3, DARK_GREY)
    display.fill_rect(20, y_start + row_height * 2, 328, 3, DARK_GREY)
    display.fill_rect(20, y_start + row_height * 3, 328, 3, DARK_GREY)
    display.fill_rect(20, y_start + row_height * 4, 328, 3, DARK_GREY)

    update_battery_values()

def update_battery_values():
    """Update just the battery values (only if changed)"""
    global battery_last_percent, battery_last_voltage, battery_last_charging, battery_last_time_remaining

    voltage = read_battery_voltage()
    charging = read_battery_charging()
    percent = read_battery_percent()

    # Update time estimate
    update_battery_time_estimate()

    y_start = 80
    row_height = 45

    # Only update if percent changed
    if percent != battery_last_percent:
        battery_last_percent = percent
        display.fill_rect(30, y_start + 10, 300, 30, BLACK)
        level_text = f"LEVEL: {percent}%"
        draw_text(display, level_text, 30, y_start + 15, GREY, 3, CODE_FONT)

    # Only update if voltage changed
    if voltage != battery_last_voltage:
        battery_last_voltage = voltage
        y2 = y_start + row_height
        display.fill_rect(30, y2 + 10, 300, 30, BLACK)
        volts = voltage / 1000.0
        volt_text = f"VOLTAGE: {volts:.2f}V"
        draw_text(display, volt_text, 30, y2 + 15, GREY, 3, CODE_FONT)

    # Only update if charging status changed
    if charging != battery_last_charging:
        battery_last_charging = charging
        y3 = y_start + row_height * 2
        display.fill_rect(30, y3 + 10, 300, 30, BLACK)
        charge_text = "CHARGING: YES" if charging else "CHARGING: NO"
        draw_text(display, charge_text, 30, y3 + 15, GREY, 3, CODE_FONT)

    # Time remaining (update if changed)
    if battery_time_remaining != battery_last_time_remaining:
        battery_last_time_remaining = battery_time_remaining
        y4 = y_start + row_height * 3
        display.fill_rect(30, y4 + 10, 300, 30, BLACK)
        if battery_time_remaining == -2:
            time_text = "FULL"
        elif battery_time_remaining <= -100:
            charge_mins = -(battery_time_remaining + 100)
            if charge_mins <= 0:
                time_text = "ALMOST FULL"
            else:
                time_text = f"FULL IN: {charge_mins}M"
        elif battery_time_remaining == 0:
            time_text = "TIME: CALCULATING..."
        elif battery_time_remaining >= 9999:
            time_text = "TIME: >16H"
        else:
            hours = battery_time_remaining // 60
            minutes = battery_time_remaining % 60
            time_text = f"TIME: {hours}H {minutes}M"
        draw_text(display, time_text, 30, y4 + 15, GREY, 3, CODE_FONT)

def draw_brightness_settings():
    display.fill(BLACK)
    draw_text(display, "BRIGHTNESS", 100, 15, GREY, 3, CODE_FONT)
    arrow_y = 120
    cx = 184
    for i in range(20):
        display.fill_rect(cx - i, arrow_y + i, i * 2 + 1, 3, GREY)
    y_center = 200
    level_text = f"{brightness_level}%"
    text_width = len(level_text) * 6 * 5
    center_x = (368 - text_width) // 2
    draw_text(display, level_text, center_x, y_center, GREY, 5, CODE_FONT)
    arrow_y = 300
    for i in range(20):
        display.fill_rect(cx - i, arrow_y + 20 - i, i * 2 + 1, 3, GREY)

def draw_volume_settings():
    display.fill(BLACK)
    draw_text(display, "VOLUME", 140, 15, GREY, 3, CODE_FONT)
    arrow_y = 120
    cx = 184
    for i in range(20):
        display.fill_rect(cx - i, arrow_y + i, i * 2 + 1, 3, GREY)
    y_center = 200
    level_text = f"{volume_level}%"
    text_width = len(level_text) * 6 * 5
    center_x = (368 - text_width) // 2
    draw_text(display, level_text, center_x, y_center, GREY, 5, CODE_FONT)
    arrow_y = 300
    for i in range(20):
        display.fill_rect(cx - i, arrow_y + 20 - i, i * 2 + 1, 3, GREY)

def days_in_month(y, m):
    if m in (1,3,5,7,8,10,12): return 31
    if m in (4,6,9,11): return 30
    if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0): return 29
    return 28

def draw_time_settings():
    global time_set_h, time_set_m, time_set_y, time_set_mo, time_set_d
    h, m, _ = read_rtc()
    y, mo, d = read_date_rtc()
    time_set_h = h
    time_set_m = m
    time_set_y = y
    time_set_mo = mo
    time_set_d = d
    display.fill(BLACK)
    draw_text(display, "SET TIME", 120, 15, GREY, 3, CODE_FONT)
    # Hour/minute up arrows
    cx1 = 80
    cx2 = 268
    for i in range(12):
        display.fill_rect(cx1 - i, 95 - i, i * 2 + 1, 2, GREY)
        display.fill_rect(cx2 - i, 95 - i, i * 2 + 1, 2, GREY)
    # Hour/minute down arrows
    for i in range(12):
        display.fill_rect(cx1 - i, 185 + i, i * 2 + 1, 2, GREY)
        display.fill_rect(cx2 - i, 185 + i, i * 2 + 1, 2, GREY)
    # Date up arrows
    dx1 = 60
    dx2 = 184
    dx3 = 308
    for i in range(10):
        display.fill_rect(dx1 - i, 255 - i, i * 2 + 1, 2, GREY)
        display.fill_rect(dx2 - i, 255 - i, i * 2 + 1, 2, GREY)
        display.fill_rect(dx3 - i, 255 - i, i * 2 + 1, 2, GREY)
    # Date down arrows
    for i in range(10):
        display.fill_rect(dx1 - i, 335 + i, i * 2 + 1, 2, GREY)
        display.fill_rect(dx2 - i, 335 + i, i * 2 + 1, 2, GREY)
        display.fill_rect(dx3 - i, 335 + i, i * 2 + 1, 2, GREY)
    # Colon between HH:MM
    draw_text(display, ":", 172, 125, GREEN, 5, CODE_FONT)
    # Dashes in date
    draw_text(display, "-", 120, 285, GREEN, 3, CODE_FONT)
    draw_text(display, "-", 237, 285, GREEN, 3, CODE_FONT)
    # SAVE button
    display.fill_rect(84, 390, 200, 45, GREEN)
    stw = len("SAVE") * 6 * 3
    draw_text(display, "SAVE", 84 + (200 - stw) // 2, 402, WHITE, 3, CODE_FONT)
    draw_time_values()

def draw_time_values():
    # Clear and redraw time
    display.fill_rect(30, 115, 140, 50, BLACK)
    display.fill_rect(198, 115, 140, 50, BLACK)
    ht = f"{time_set_h:02d}"
    mt = f"{time_set_m:02d}"
    htw = len(ht) * 6 * 5
    mtw = len(mt) * 6 * 5
    draw_text(display, ht, 80 - htw // 2, 125, GREEN, 5, CODE_FONT)
    draw_text(display, mt, 268 - mtw // 2, 125, GREEN, 5, CODE_FONT)
    # Clear and redraw date
    display.fill_rect(15, 278, 110, 30, BLACK)
    display.fill_rect(140, 278, 80, 30, BLACK)
    display.fill_rect(255, 278, 98, 30, BLACK)
    yt = f"{time_set_y}"
    mot = f"{time_set_mo:02d}"
    dt = f"{time_set_d:02d}"
    ytw = len(yt) * 6 * 3
    motw = len(mot) * 6 * 3
    dtw = len(dt) * 6 * 3
    draw_text(display, yt, 60 - ytw // 2, 285, GREEN, 3, CODE_FONT)
    draw_text(display, mot, 184 - motw // 2, 285, GREEN, 3, CODE_FONT)
    draw_text(display, dt, 308 - dtw // 2, 285, GREEN, 3, CODE_FONT)

def draw_about_settings():
    display.fill(BLACK)
    draw_text(display, "ABOUT", 148, 15, GREY, 3, CODE_FONT)
    y = 80
    rh = 45
    gc.collect()
    free_kb = gc.mem_free() // 1024
    total_kb = 512  # ESP32-S3 has ~512KB usable
    used_kb = total_kb - free_kb
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"FREE RAM: {free_kb}KB", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"USED RAM: {used_kb}KB", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    uptime_s = time.ticks_ms() // 1000
    up_m = uptime_s // 60
    up_h = up_m // 60
    up_m = up_m % 60
    draw_text(display, f"UPTIME: {up_h}H {up_m}M", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "APPS: 33", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "DISPLAY: 368x448", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "CHIP: ESP32-S3", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    # Updates button - centered, wider
    btn_w = 200
    btn_x = (368 - btn_w) // 2
    display.fill_rect(btn_x, 400, btn_w, 40, GREEN)
    txt = "VIEW UPDATES"
    txt_w = len(txt) * 6 * 2
    draw_text(display, txt, btn_x + (btn_w - txt_w) // 2, 410, WHITE, 2, CODE_FONT)

# Changelog reader
changelog_pos = 0
changelog_lines = []
CL_LINES = 14
CL_CHARS = 19

def changelog_read_page(pos):
    """Read one page of changelog from local flash"""
    lines = []
    try:
        f = open("changelog.txt", "r")
        f.seek(pos)
        cur_line = ""
        cur_word = ""
        word_pos = pos
        while len(lines) < CL_LINES:
            p = f.tell()
            ch = f.read(1)
            if not ch:
                if cur_word:
                    if len(cur_line) + len(cur_word) + 1 <= CL_CHARS:
                        cur_line = cur_line + " " + cur_word if cur_line else cur_word
                    else:
                        if cur_line:
                            lines.append(cur_line)
                        cur_line = cur_word
                if cur_line:
                    lines.append(cur_line)
                nxt = f.tell()
                f.close()
                return lines, nxt, True
            if ch == '\r':
                continue
            elif ch == '\n' or ch == ' ':
                if cur_word:
                    if len(cur_line) + len(cur_word) + 1 <= CL_CHARS:
                        cur_line = cur_line + " " + cur_word if cur_line else cur_word
                    else:
                        if cur_line:
                            lines.append(cur_line)
                            if len(lines) >= CL_LINES:
                                f.close()
                                return lines, word_pos, False
                        cur_line = cur_word
                    cur_word = ""
                if ch == '\n' and cur_line:
                    lines.append(cur_line)
                    cur_line = ""
            else:
                if not cur_word:
                    word_pos = p
                cur_word += ch
        if cur_word:
            f.close()
            return lines, word_pos, False
        nxt = f.tell()
        f.close()
        return lines, nxt, False
    except:
        return ["FILE NOT FOUND", "UPLOAD CHANGELOG.TXT"], 0, True

def changelog_prev_pos(target):
    """Find previous page start"""
    if target <= 0:
        return 0
    est = CL_LINES * CL_CHARS * 3
    start = max(0, target - est)
    try:
        f = open("changelog.txt", "r")
        f.seek(start)
        positions = [start]
        cur_line = ""
        cur_word = ""
        line_count = 0
        word_pos = start
        while f.tell() < target:
            p = f.tell()
            ch = f.read(1)
            if not ch:
                break
            if ch == '\r':
                continue
            elif ch == '\n' or ch == ' ':
                if cur_word:
                    if len(cur_line) + len(cur_word) + 1 <= CL_CHARS:
                        cur_line = cur_line + " " + cur_word if cur_line else cur_word
                    else:
                        if cur_line:
                            line_count += 1
                            if line_count >= CL_LINES:
                                positions.append(word_pos)
                                line_count = 0
                        cur_line = cur_word
                    cur_word = ""
                if ch == '\n' and cur_line:
                    line_count += 1
                    cur_line = ""
                    if line_count >= CL_LINES:
                        positions.append(f.tell())
                        line_count = 0
            else:
                if not cur_word:
                    word_pos = p
                cur_word += ch
        f.close()
        if len(positions) >= 2:
            return positions[-2]
        return 0
    except:
        return 0

def draw_changelog():
    """Draw changelog page"""
    global changelog_pos
    display.fill(BLACK)
    lines, nxt, eof = changelog_read_page(changelog_pos)
    y = 12
    for line in lines:
        draw_text(display, line, 10, y, GREY, 3, BOOK_FONT)
        y += 28
    # Position indicator at bottom (like book reader)
    if changelog_pos == 0:
        pos_text = "START"
    elif eof:
        pos_text = "END"
    else:
        pos_text = f"POS {changelog_pos}"
    tw = len(pos_text) * 6 * 2
    draw_text(display, pos_text, (368 - tw) // 2, 420, DARK_GREY, 2, CODE_FONT)
    return nxt, eof

def draw_steps_settings():
    """Draw step counter settings screen"""
    display.fill(BLACK)
    draw_text(display, "STEP COUNTER", 80, 15, GREY, 3, CODE_FONT)
    # On/Off toggle button
    y_toggle = 100
    display.fill_rect(84, y_toggle, 200, 60, GREEN if steps_enabled else DARK_GREY)
    toggle_text = "ON" if steps_enabled else "OFF"
    draw_text(display, toggle_text, 155, y_toggle + 18, WHITE, 3, CODE_FONT)
    # Current step count
    y_count = 200
    draw_text(display, "TODAY", 145, y_count, GREY, 2, CODE_FONT)
    count_text = str(step_count)
    text_width = len(count_text) * 6 * 5
    center_x = (368 - text_width) // 2
    draw_text(display, count_text, center_x, y_count + 35, GREEN, 5, CODE_FONT)
    # Reset button
    display.fill_rect(114, 340, 140, 50, DARK_GREY)
    draw_text(display, "RESET", 145, 355, GREY, 2, CODE_FONT)

def save_steps_settings():
    """Save step counter settings"""
    try:
        with open("steps.txt", "w") as f:
            f.write(f"{1 if steps_enabled else 0}\n")
            f.write(f"{step_count}\n")
    except:
        pass

def load_steps_settings():
    """Load step counter settings"""
    global steps_enabled, step_count
    try:
        with open("steps.txt", "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                steps_enabled = int(lines[0].strip()) == 1
                step_count = int(lines[1].strip())
    except:
        pass

def detect_step():
    """Detect steps using accelerometer - call from main loop when enabled"""
    global step_count, step_last_mag, step_last_time
    ax, ay, az = read_accel()
    # Calculate magnitude (math already imported above)
    mag = math.sqrt(ax*ax + ay*ay + az*az)
    now = time.ticks_ms()
    # Detect step: magnitude crosses threshold going up, with debounce
    if step_last_mag < step_threshold and mag >= step_threshold:
        if time.ticks_diff(now, step_last_time) > step_debounce:
            step_count += 1
            step_last_time = now
            # Save periodically (every 10 steps to reduce writes)
            if step_count % 10 == 0:
                save_steps_settings()
    step_last_mag = mag

# Stats menu items
STATS_ITEMS = ["2048", "BATTLESHIP", "BRICK BREAKER", "CHECKERS", "CHESS", "CONNECT FOUR", "FLAPPY BIRD", "GEOMETRY DASH", "MASTERMIND", "MAZE", "MINESWEEPER", "PONG", "SLIDING PUZZLE", "SNAKE", "SPACE INVADERS", "SUDOKU", "TIC-TAC-TOE", "UNFAIR FLIPS", "WORD SEARCH", "WORDLE"]
stats_scroll = 0
STATS_PER_PAGE = 6

def draw_stats_menu():
    display.fill(BLACK)
    draw_text(display, "STATS", 140, 15, GREY, 3, CODE_FONT)
    y_start = 80
    row_height = 50
    for idx in range(STATS_PER_PAGE):
        item_idx = stats_scroll + idx
        if item_idx >= len(STATS_ITEMS):
            break
        y = y_start + idx * row_height
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, STATS_ITEMS[item_idx], 30, y + 15, GREY, 3, CODE_FONT)
    visible_count = min(STATS_PER_PAGE, len(STATS_ITEMS) - stats_scroll)
    y_final = y_start + visible_count * row_height
    display.fill_rect(20, y_final, 328, 3, DARK_GREY)
    cx = 184
    if stats_scroll > 0:
        for i in range(10):
            display.fill_rect(cx - i, 55 + i, i * 2 + 1, 2, GREY)
    if stats_scroll + STATS_PER_PAGE < len(STATS_ITEMS):
        for i in range(10):
            display.fill_rect(cx - i, y_final + 15 + 10 - i, i * 2 + 1, 2, GREY)
# 2048 stats (persist to file)
high_score_2048 = 0
highest_tile_2048 = 0

# Battleship stats - per difficulty for AI, plus PvP
bship_easy_wins = 0    # Player wins on easy
bship_easy_losses = 0  # AI wins on easy
bship_med_wins = 0     # Player wins on medium
bship_med_losses = 0   # AI wins on medium
bship_hard_wins = 0    # Player wins on hard
bship_hard_losses = 0  # AI wins on hard
bship_p1_wins = 0  # P1 wins in 1v1
bship_p2_wins = 0  # P2 wins in 1v1

# Pong stats - per difficulty + PvP
pong_easy_wins = 0
pong_easy_losses = 0
pong_med_wins = 0
pong_med_losses = 0
pong_hard_wins = 0
pong_hard_losses = 0
pong_imp_wins = 0
pong_imp_losses = 0
pong_p1_wins = 0
pong_p2_wins = 0
pong_stats_page = 0

# Mastermind stats (0 for best = no record yet)
mm_wins = 0
mm_losses = 0
mm_best = 0  # Fewest guesses to win

# Asteroids stats
ast_high_score = 0
ast_total_games = 0
ast_best_wave = 0

# Brick Breaker stats
brick_high_score = 0
brick_levels_cleared = 0

# Checkers stats
chk_easy_wins = 0
chk_easy_losses = 0
chk_med_wins = 0
chk_med_losses = 0
chk_hard_wins = 0
chk_hard_losses = 0
chk_p1_wins = 0
chk_p2_wins = 0

# Connect 4 stats
c4_easy_wins = 0
c4_easy_losses = 0
c4_med_wins = 0
c4_med_losses = 0
c4_hard_wins = 0
c4_hard_losses = 0
c4_p1_wins = 0
c4_p2_wins = 0
c4_draws = 0

# Jigsaw stats
jg_3_wins = 0
jg_3_best = 0
jg_4_wins = 0
jg_4_best = 0
jg_5_wins = 0
jg_5_best = 0

# Pac-Man stats
pac_high_score = 0
pac_total_games = 0
pac_best_level = 0

# Sliding Puzzle stats
sl_3_best_moves = 0
sl_3_best_time = 0
sl_3_wins = 0
sl_4_best_moves = 0
sl_4_best_time = 0
sl_4_wins = 0
sl_5_best_moves = 0
sl_5_best_time = 0
sl_5_wins = 0

# Simon Says stats
sim_high_score = 0
sim_total_games = 0

# Whack-a-Mole stats
wak_high_score = 0
wak_total_games = 0
wak_best_combo = 0

# Word Search stats
ws_easy_wins = 0
ws_med_wins = 0
ws_hard_wins = 0
ws_easy_best = 0
ws_med_best = 0
ws_hard_best = 0

def save_all_stats():
    try:
        f = open("all_stats.txt", "w")
        f.write(f"2048_high={high_score_2048}\n2048_tile={highest_tile_2048}\n")
        f.write(f"bship_ew={bship_easy_wins}\nbship_el={bship_easy_losses}\n")
        f.write(f"bship_mw={bship_med_wins}\nbship_ml={bship_med_losses}\n")
        f.write(f"bship_hw={bship_hard_wins}\nbship_hl={bship_hard_losses}\n")
        f.write(f"bship_p1={bship_p1_wins}\nbship_p2={bship_p2_wins}\n")
        f.write(f"brick_high={brick_high_score}\nbrick_levels={brick_levels_cleared}\n")
        f.write(f"chk_ew={chk_easy_wins}\nchk_el={chk_easy_losses}\n")
        f.write(f"chk_mw={chk_med_wins}\nchk_ml={chk_med_losses}\n")
        f.write(f"chk_hw={chk_hard_wins}\nchk_hl={chk_hard_losses}\n")
        f.write(f"chk_p1={chk_p1_wins}\nchk_p2={chk_p2_wins}\n")
        f.write(f"c4_ew={c4_easy_wins}\nc4_el={c4_easy_losses}\n")
        f.write(f"c4_mw={c4_med_wins}\nc4_ml={c4_med_losses}\n")
        f.write(f"c4_hw={c4_hard_wins}\nc4_hl={c4_hard_losses}\n")
        f.write(f"c4_p1={c4_p1_wins}\nc4_p2={c4_p2_wins}\nc4_dr={c4_draws}\n")
        f.write(f"chess_p1={chess_p1_wins}\nchess_p2={chess_p2_wins}\nchess_draws={chess_draws}\n")
        f.write(f"chess_hw={chess_human_wins}\nchess_aw={chess_ai_wins}\nchess_ad={chess_ai_draws}\n")
        f.write(f"flappy_high={flappy_high}\nflappy_games={flappy_games}\n")
        f.write(f"gforce_high={gforce_high:.1f}\n")
        f.write(f"mm_wins={mm_wins}\nmm_losses={mm_losses}\nmm_best={mm_best}\n")
        f.write(f"ms_eb={ms_easy_best}\nms_ew={ms_easy_wins}\nms_el={ms_easy_losses}\n")
        f.write(f"ms_mb={ms_med_best}\nms_mw={ms_med_wins}\nms_ml={ms_med_losses}\n")
        f.write(f"ms_hb={ms_hard_best}\nms_hw={ms_hard_wins}\nms_hl={ms_hard_losses}\n")
        f.write(f"pong_ew={pong_easy_wins}\npong_el={pong_easy_losses}\n")
        f.write(f"pong_mw={pong_med_wins}\npong_ml={pong_med_losses}\n")
        f.write(f"pong_hw={pong_hard_wins}\npong_hl={pong_hard_losses}\n")
        f.write(f"pong_p1={pong_p1_wins}\npong_p2={pong_p2_wins}\n")
        f.write(f"pong_iw={pong_imp_wins}\npong_il={pong_imp_losses}\n")
        f.write(f"snake_high={snake_high_score}\n")
        f.write(f"sdk_eb={sdk_easy_best}\nsdk_ew={sdk_easy_wins}\nsdk_el={sdk_easy_losses}\n")
        f.write(f"sdk_mb={sdk_med_best}\nsdk_mw={sdk_med_wins}\nsdk_ml={sdk_med_losses}\n")
        f.write(f"sdk_hb={sdk_hard_best}\nsdk_hw={sdk_hard_wins}\nsdk_hl={sdk_hard_losses}\n")
        f.write(f"wrd_games={wrd_games}\nwrd_wins={wrd_wins}\n")
        f.write(f"wrd_streak={wrd_streak}\nwrd_max={wrd_max_streak}\nwrd_last={wrd_last_win}\n")
        f.write(f"wrd_played={wrd_last_played}\n")
        f.write(f"wrd_p1w={wrd_pvp_p1_wins}\nwrd_p2w={wrd_pvp_p2_wins}\nwrd_draws={wrd_pvp_draws}\n")
        f.write(f"flp_coins={flips_coins}\nflp_best={flips_best_streak}\n")
        f.write(f"flp_flips={flips_total_flips}\nflp_heads={flips_total_heads}\n")
        f.write(f"flp_wins={flips_wins}\n")
        f.write(f"flp_clv={flips_chance_lv}\nflp_vlv={flips_value_lv}\nflp_mlv={flips_combo_lv}\n")
        f.write(f"si_high={si_high_score}\nsi_kills={si_total_kills}\n")
        f.write(f"si_games={si_total_games}\nsi_best_wave={si_best_wave}\n")
        f.write(f"mz_eb={mz_easy_best}\nmz_ew={mz_easy_wins}\n")
        f.write(f"mz_mb={mz_med_best}\nmz_mw={mz_med_wins}\n")
        f.write(f"mz_hb={mz_hard_best}\nmz_hw={mz_hard_wins}\n")
        f.write(f"ttt_ew={ttt_easy_wins}\nttt_el={ttt_easy_losses}\n")
        f.write(f"ttt_mw={ttt_med_wins}\nttt_ml={ttt_med_losses}\n")
        f.write(f"ttt_hw={ttt_hard_wins}\nttt_hl={ttt_hard_losses}\n")
        f.write(f"ttt_xw={ttt_pvp_x_wins}\nttt_ow={ttt_pvp_o_wins}\nttt_dr={ttt_draws}\n")
        f.write(f"gd_att={gd_attempts}\ngd_comp={gd_completions}\ngd_best={gd_best_pct}\n")
        # ast stats removed
        f.write(f"sl_3m={sl_3_best_moves}\nsl_3t={sl_3_best_time}\nsl_3w={sl_3_wins}\n")
        f.write(f"sl_4m={sl_4_best_moves}\nsl_4t={sl_4_best_time}\nsl_4w={sl_4_wins}\n")
        f.write(f"sl_5m={sl_5_best_moves}\nsl_5t={sl_5_best_time}\nsl_5w={sl_5_wins}\n")
        # sim/wak stats removed
        f.write(f"ws_ew={ws_easy_wins}\nws_mw={ws_med_wins}\nws_hw={ws_hard_wins}\n")
        f.write(f"ws_eb={ws_easy_best}\nws_mb={ws_med_best}\nws_hb={ws_hard_best}\n")
        f.close()
    except:
        pass

def load_all_stats():
    global high_score_2048, highest_tile_2048
    global bship_easy_wins, bship_easy_losses, bship_med_wins, bship_med_losses
    global bship_hard_wins, bship_hard_losses, bship_p1_wins, bship_p2_wins
    global brick_high_score, brick_levels_cleared
    global chk_easy_wins, chk_easy_losses, chk_med_wins, chk_med_losses
    global chk_hard_wins, chk_hard_losses, chk_p1_wins, chk_p2_wins
    global c4_easy_wins, c4_easy_losses, c4_med_wins, c4_med_losses
    global c4_hard_wins, c4_hard_losses, c4_p1_wins, c4_p2_wins, c4_draws
    global chess_p1_wins, chess_p2_wins, chess_draws, chess_human_wins, chess_ai_wins, chess_ai_draws
    global flappy_high, flappy_games
    global gforce_high
    global mm_wins, mm_losses, mm_best
    global ms_easy_best, ms_easy_wins, ms_easy_losses
    global ms_med_best, ms_med_wins, ms_med_losses
    global ms_hard_best, ms_hard_wins, ms_hard_losses
    global pong_easy_wins, pong_easy_losses, pong_med_wins, pong_med_losses
    global pong_hard_wins, pong_hard_losses, pong_imp_wins, pong_imp_losses, pong_p1_wins, pong_p2_wins
    global snake_high_score
    global sdk_easy_best, sdk_easy_wins, sdk_easy_losses
    global sdk_med_best, sdk_med_wins, sdk_med_losses
    global sdk_hard_best, sdk_hard_wins, sdk_hard_losses
    global wrd_games, wrd_wins, wrd_streak, wrd_max_streak, wrd_last_win, wrd_last_played
    global wrd_pvp_p1_wins, wrd_pvp_p2_wins, wrd_pvp_draws
    global flips_coins, flips_best_streak, flips_total_flips, flips_total_heads
    global flips_wins, flips_chance_lv, flips_value_lv, flips_combo_lv
    global si_high_score, si_total_kills, si_total_games, si_best_wave
    global mz_easy_best, mz_easy_wins, mz_med_best, mz_med_wins, mz_hard_best, mz_hard_wins
    global ttt_easy_wins, ttt_easy_losses, ttt_med_wins, ttt_med_losses
    global ttt_hard_wins, ttt_hard_losses, ttt_pvp_x_wins, ttt_pvp_o_wins, ttt_draws
    global gd_attempts, gd_completions, gd_best_pct
    global ast_high_score, ast_total_games, ast_best_wave
    global sl_3_best_moves, sl_3_best_time, sl_3_wins
    global sl_4_best_moves, sl_4_best_time, sl_4_wins
    global sl_5_best_moves, sl_5_best_time, sl_5_wins
    global ws_easy_wins, ws_med_wins, ws_hard_wins, ws_easy_best, ws_med_best, ws_hard_best
    # Try unified file first
    try:
        f = open("all_stats.txt", "r")
        d = {}
        for line in f:
            line = line.strip()
            if "=" in line:
                k, v = line.split("=", 1)
                d[k] = v
        f.close()
        high_score_2048 = int(d.get("2048_high", "0"))
        highest_tile_2048 = int(d.get("2048_tile", "0"))
        bship_easy_wins = int(d.get("bship_ew", "0"))
        bship_easy_losses = int(d.get("bship_el", "0"))
        bship_med_wins = int(d.get("bship_mw", "0"))
        bship_med_losses = int(d.get("bship_ml", "0"))
        bship_hard_wins = int(d.get("bship_hw", "0"))
        bship_hard_losses = int(d.get("bship_hl", "0"))
        bship_p1_wins = int(d.get("bship_p1", "0"))
        bship_p2_wins = int(d.get("bship_p2", "0"))
        brick_high_score = int(d.get("brick_high", "0"))
        brick_levels_cleared = int(d.get("brick_levels", "0"))
        chk_easy_wins = int(d.get("chk_ew", "0"))
        chk_easy_losses = int(d.get("chk_el", "0"))
        chk_med_wins = int(d.get("chk_mw", "0"))
        chk_med_losses = int(d.get("chk_ml", "0"))
        chk_hard_wins = int(d.get("chk_hw", "0"))
        chk_hard_losses = int(d.get("chk_hl", "0"))
        chk_p1_wins = int(d.get("chk_p1", "0"))
        chk_p2_wins = int(d.get("chk_p2", "0"))
        c4_easy_wins = int(d.get("c4_ew", "0"))
        c4_easy_losses = int(d.get("c4_el", "0"))
        c4_med_wins = int(d.get("c4_mw", "0"))
        c4_med_losses = int(d.get("c4_ml", "0"))
        c4_hard_wins = int(d.get("c4_hw", "0"))
        c4_hard_losses = int(d.get("c4_hl", "0"))
        c4_p1_wins = int(d.get("c4_p1", "0"))
        c4_p2_wins = int(d.get("c4_p2", "0"))
        c4_draws = int(d.get("c4_dr", "0"))
        chess_p1_wins = int(d.get("chess_p1", "0"))
        chess_p2_wins = int(d.get("chess_p2", "0"))
        chess_draws = int(d.get("chess_draws", "0"))
        chess_human_wins = int(d.get("chess_hw", "0"))
        chess_ai_wins = int(d.get("chess_aw", "0"))
        chess_ai_draws = int(d.get("chess_ad", "0"))
        flappy_high = int(d.get("flappy_high", "0"))
        flappy_games = int(d.get("flappy_games", "0"))
        gforce_high = float(d.get("gforce_high", "0.0"))
        mm_wins = int(d.get("mm_wins", "0"))
        mm_losses = int(d.get("mm_losses", "0"))
        mm_best = int(d.get("mm_best", "0"))
        ms_easy_best = int(d.get("ms_eb", "0"))
        ms_easy_wins = int(d.get("ms_ew", "0"))
        ms_easy_losses = int(d.get("ms_el", "0"))
        ms_med_best = int(d.get("ms_mb", "0"))
        ms_med_wins = int(d.get("ms_mw", "0"))
        ms_med_losses = int(d.get("ms_ml", "0"))
        ms_hard_best = int(d.get("ms_hb", "0"))
        ms_hard_wins = int(d.get("ms_hw", "0"))
        ms_hard_losses = int(d.get("ms_hl", "0"))
        pong_easy_wins = int(d.get("pong_ew", "0"))
        pong_easy_losses = int(d.get("pong_el", "0"))
        pong_med_wins = int(d.get("pong_mw", "0"))
        pong_med_losses = int(d.get("pong_ml", "0"))
        pong_hard_wins = int(d.get("pong_hw", "0"))
        pong_hard_losses = int(d.get("pong_hl", "0"))
        pong_p1_wins = int(d.get("pong_p1", "0"))
        pong_p2_wins = int(d.get("pong_p2", "0"))
        pong_imp_wins = int(d.get("pong_iw", "0"))
        pong_imp_losses = int(d.get("pong_il", "0"))
        snake_high_score = int(d.get("snake_high", "0"))
        sdk_easy_best = int(d.get("sdk_eb", "0"))
        sdk_easy_wins = int(d.get("sdk_ew", "0"))
        sdk_easy_losses = int(d.get("sdk_el", "0"))
        sdk_med_best = int(d.get("sdk_mb", "0"))
        sdk_med_wins = int(d.get("sdk_mw", "0"))
        sdk_med_losses = int(d.get("sdk_ml", "0"))
        sdk_hard_best = int(d.get("sdk_hb", "0"))
        sdk_hard_wins = int(d.get("sdk_hw", "0"))
        sdk_hard_losses = int(d.get("sdk_hl", "0"))
        wrd_games = int(d.get("wrd_games", "0"))
        wrd_wins = int(d.get("wrd_wins", "0"))
        wrd_streak = int(d.get("wrd_streak", "0"))
        wrd_max_streak = int(d.get("wrd_max", "0"))
        wrd_last_win = d.get("wrd_last", "")
        wrd_last_played = d.get("wrd_played", "")
        wrd_pvp_p1_wins = int(d.get("wrd_p1w", "0"))
        wrd_pvp_p2_wins = int(d.get("wrd_p2w", "0"))
        wrd_pvp_draws = int(d.get("wrd_draws", "0"))
        flips_coins = int(d.get("flp_coins", "0"))
        flips_best_streak = int(d.get("flp_best", "0"))
        flips_total_flips = int(d.get("flp_flips", "0"))
        flips_total_heads = int(d.get("flp_heads", "0"))
        flips_wins = int(d.get("flp_wins", "0"))
        flips_chance_lv = int(d.get("flp_clv", "0"))
        flips_value_lv = int(d.get("flp_vlv", "0"))
        flips_combo_lv = int(d.get("flp_mlv", "0"))
        si_high_score = int(d.get("si_high", "0"))
        si_total_kills = int(d.get("si_kills", "0"))
        si_total_games = int(d.get("si_games", "0"))
        si_best_wave = int(d.get("si_best_wave", "0"))
        mz_easy_best = int(d.get("mz_eb", "0"))
        mz_easy_wins = int(d.get("mz_ew", "0"))
        mz_med_best = int(d.get("mz_mb", "0"))
        mz_med_wins = int(d.get("mz_mw", "0"))
        mz_hard_best = int(d.get("mz_hb", "0"))
        mz_hard_wins = int(d.get("mz_hw", "0"))
        ttt_easy_wins = int(d.get("ttt_ew", "0"))
        ttt_easy_losses = int(d.get("ttt_el", "0"))
        ttt_med_wins = int(d.get("ttt_mw", "0"))
        ttt_med_losses = int(d.get("ttt_ml", "0"))
        ttt_hard_wins = int(d.get("ttt_hw", "0"))
        ttt_hard_losses = int(d.get("ttt_hl", "0"))
        ttt_pvp_x_wins = int(d.get("ttt_xw", "0"))
        ttt_pvp_o_wins = int(d.get("ttt_ow", "0"))
        ttt_draws = int(d.get("ttt_dr", "0"))
        gd_attempts = int(d.get("gd_att", "0"))
        gd_completions = int(d.get("gd_comp", "0"))
        gd_best_pct = int(d.get("gd_best", "0"))
        ast_high_score = int(d.get("ast_hs", "0"))
        ast_total_games = int(d.get("ast_tg", "0"))
        ast_best_wave = int(d.get("ast_bw", "0"))
        sl_3_best_moves = int(d.get("sl_3m", "0"))
        sl_3_best_time = int(d.get("sl_3t", "0"))
        sl_3_wins = int(d.get("sl_3w", "0"))
        sl_4_best_moves = int(d.get("sl_4m", "0"))
        sl_4_best_time = int(d.get("sl_4t", "0"))
        sl_4_wins = int(d.get("sl_4w", "0"))
        sl_5_best_moves = int(d.get("sl_5m", "0"))
        sl_5_best_time = int(d.get("sl_5t", "0"))
        sl_5_wins = int(d.get("sl_5w", "0"))
        # sim/wak stats removed
        ws_easy_wins = int(d.get("ws_ew", "0"))
        ws_med_wins = int(d.get("ws_mw", "0"))
        ws_hard_wins = int(d.get("ws_hw", "0"))
        ws_easy_best = int(d.get("ws_eb", "0"))
        ws_med_best = int(d.get("ws_mb", "0"))
        ws_hard_best = int(d.get("ws_hb", "0"))
        print("Loaded all stats")
        return
    except:
        print("Error loading stats - file may not exist yet")

def save_stats():
    save_all_stats()

def save_bship_stats():
    save_all_stats()

def save_pong_stats():
    save_all_stats()

def save_mm_stats():
    save_all_stats()

def save_snake_stats():
    save_all_stats()

def save_brick_stats():
    save_all_stats()

def save_flips_stats():
    save_all_stats()

def save_invaders_stats():
    save_all_stats()

def save_chk_stats():
    save_all_stats()

def save_c4_stats():
    save_all_stats()

def save_ast_stats():
    save_all_stats()

def save_jg_stats():
    save_all_stats()

def save_pac_stats():
    save_all_stats()

def save_sl_stats():
    save_all_stats()

def save_ws_stats():
    save_all_stats()
def get_swipe_direction(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) < 20 and abs(dy) < 20:  # Min swipe distance
        return -1
    if abs(dx) > abs(dy):
        return 1 if dx > 0 else 3
    else:
        return 2 if dy > 0 else 0


# ===== LOAD GAME MODULES =====
for _gf in ["2048","battleship","books","brick","calculator","checkers","chess",
            "clock","connect4","draw","flappy","flips","gdash","invaders","life","gyro","laser",
            "mastermind","maze","minesweeper","notes","photos","pong","sliding",
            "snake","sudoku","tictactoe","wordsearch","wordle"]:
    exec(open("games/game_" + _gf + ".py").read())

load_all_stats()
load_steps_settings()
load_safe_mode()
load_docs_mode()
load_globe_setting()
load_app_sort()

# ===== SCREEN STATE =====
SCREEN_GLOBE = 0
SCREEN_MENU = 1
SCREEN_APP = 2
SCREEN_CATEGORIES = 3

app_scroll = 0  # Scroll offset for app menu

current_screen = SCREEN_GLOBE
current_app = -1
settings_submenu = -1
settings_scroll = 0
stats_submenu = -1
reading_changelog = False
cl_next_pos = 0
cl_eof = False
showing_win_screen = False
showing_death_screen = False
reading_book = False  # True when reading a book, False when in book selection
last_activity = time.ticks_ms()
last_time_text = ""
last_date_text = ""
IDLE_TIMEOUT = 30000

ball_x, ball_y = 184, 220
filtered_ax, filtered_ay = 0.0, 0.0
swipe_start_x, swipe_start_y = 0, 0
touch_was_pressed = False
hold_start_time = None

# ===== MAIN LOOP =====
print("Starting!")
draw_globe_screen()

try:
    while True:
        touch = read_touch()
        now = time.ticks_ms()
        touch_pressed = touch is not None
        touch_just_pressed = touch_pressed and not touch_was_pressed
        touch_was_pressed = touch_pressed

        # Check BOOT button (hold for 1.25 seconds to return to globe)
        # ONLY if not already on globe screen (prevents flash when turning off!)
        if current_screen != SCREEN_GLOBE:
            boot_state = boot_button.value() == 0  # 0 = pressed (active LOW)
            if boot_state and not boot_button_pressed:
                # Button just pressed - start timer
                boot_button_pressed = True
                boot_button_start_time = now
            elif boot_state and boot_button_pressed:
                # Button held - check if 1.25 seconds elapsed
                if time.ticks_diff(now, boot_button_start_time) >= 180:
                    # Go to globe screen
                    if current_app == 14:
                        laser_off()
                    if current_app >= 0 and current_app < len(APPS):
                        track_app_exit(APPS[current_app])
                    current_screen = SCREEN_GLOBE
                    current_app = -1
                    draw_globe_screen()
                    last_time_text = ""
                    last_date_text = ""
                    boot_button_pressed = False  # Reset
            elif not boot_state:
                # Button released
                boot_button_pressed = False
        else:
            # On globe screen - reset button state
            boot_button_pressed = False

        if current_screen == SCREEN_GLOBE:
            if touch_just_pressed:
                last_activity = now
                while read_touch() is not None:
                    time.sleep_ms(50)
                if app_sort_mode == 1:
                    current_screen = SCREEN_CATEGORIES
                    menu_category = -1
                    draw_category_screen()
                else:
                    current_screen = SCREEN_MENU
                    draw_menu_screen()
                last_time_text = ""

        elif current_screen == SCREEN_CATEGORIES:
            if touch_just_pressed and touch is not None:
                tx, ty = touch
                last_activity = now
                while read_touch() is not None:
                    time.sleep_ms(10)
                # 2x2 grid button hit test (match draw_category_screen layout)
                gap = 8
                bw = (368 - gap * 3) // 2
                bh = (448 - 55 - gap * 3) // 2
                x1 = gap
                x2 = gap * 2 + bw
                y1 = 55
                y2 = 55 + bh + gap
                cat_hit = -1
                if y1 <= ty <= y1 + bh:
                    if x1 <= tx <= x1 + bw:
                        cat_hit = 0
                    elif x2 <= tx <= x2 + bw:
                        cat_hit = 1
                elif y2 <= ty <= y2 + bh:
                    if x1 <= tx <= x1 + bw:
                        cat_hit = 2
                    elif x2 <= tx <= x2 + bw:
                        cat_hit = 3
                if cat_hit >= 0:
                    menu_category = cat_hit
                    app_scroll = 0
                    current_screen = SCREEN_MENU
                    draw_menu_screen()
            if time.ticks_diff(now, last_activity) > IDLE_TIMEOUT:
                current_screen = SCREEN_GLOBE
                draw_globe_screen()
                last_time_text = ""

        elif current_screen == SCREEN_MENU:
            if touch_just_pressed and touch is not None:
                tx, ty = touch
                last_activity = now
                while read_touch() is not None:
                    time.sleep_ms(50)
                # Tap category label at top to go back to categories
                if app_sort_mode == 1 and menu_category >= 0 and 40 <= ty <= 65:
                    current_screen = SCREEN_CATEGORIES
                    menu_category = -1
                    draw_category_screen()
                    continue
                y_start = 80
                row_height = 50
                max_visible = 7
                if app_sort_mode == 1 and menu_category >= 0:
                    vis = get_category_apps(menu_category)
                else:
                    vis = get_visible_apps()
                # Slightly bigger hitbox: include top 10px of first item and bottom 10px of last item
                if ty < y_start + 10 and app_scroll > 0:
                    app_scroll = max(0, app_scroll - max_visible)
                    draw_menu_screen()
                elif ty > y_start + max_visible * row_height - 10 and app_scroll + max_visible < len(vis):
                    app_scroll = min(len(vis) - max_visible, app_scroll + max_visible)
                    draw_menu_screen()
                else:
                    for idx in range(max_visible):
                        vi = app_scroll + idx
                        if vi >= len(vis):
                            break
                        app_idx = vis[vi]
                        app_top = y_start + idx * row_height
                        app_bottom = app_top + row_height
                        if app_top < ty < app_bottom:
                            current_app = app_idx
                            current_screen = SCREEN_APP
                            track_app_enter()
                            if app_idx == 0: launch_2048()
                            elif app_idx == 1: launch_battleship()
                            elif app_idx == 2: launch_books()
                            elif app_idx == 3: launch_brick()
                            elif app_idx == 4: launch_calculator()
                            elif app_idx == 5: launch_checkers()
                            elif app_idx == 6: launch_chess()
                            elif app_idx == 7: launch_clock()
                            elif app_idx == 8: launch_connect4()
                            elif app_idx == 9: launch_draw()
                            elif app_idx == 10: launch_flappy()
                            elif app_idx == 11: launch_life()
                            elif app_idx == 12: launch_gdash()
                            elif app_idx == 13: launch_gyro()
                            elif app_idx == 14: launch_laser()
                            elif app_idx == 15: launch_mastermind()
                            elif app_idx == 16: launch_maze()
                            elif app_idx == 17: launch_minesweeper()
                            elif app_idx == 18: launch_notes()
                            elif app_idx == 19: launch_photos()
                            elif app_idx == 20: launch_pong()
                            elif app_idx == 21: launch_sliding()
                            elif app_idx == 22: launch_snake()
                            elif app_idx == 23: launch_invaders()
                            elif app_idx == 24: launch_sudoku()
                            elif app_idx == 25: launch_tictactoe()
                            elif app_idx == 26: launch_flips()
                            elif app_idx == 27: launch_wordsearch()
                            elif app_idx == 28: launch_wordle()
                            elif app_idx == 29:
                                settings_submenu = -1
                                settings_scroll = 0
                                draw_settings_app()
                            break
            if time.ticks_diff(now, last_activity) > IDLE_TIMEOUT:
                current_screen = SCREEN_GLOBE
                draw_globe_screen()
                last_time_text = ""

        elif current_screen == SCREEN_APP:
            # Skip blocking touch handler for continuous games
            if current_app == 20 and pong_mode == 1:
                pass
            elif current_app == 10 and flappy_running:
                pass
            elif current_app == 3 and brick_mode == 1:
                pass
            elif current_app == 9 and draw_mode == 2:
                pass
            elif current_app == 9 and draw_mode == 3:
                pass
            elif current_app == 11 and not life_running:
                pass
            elif current_app == 12 and gd_mode == 1:
                pass
            elif current_app == 23 and si_mode == 0:
                pass
            elif touch_just_pressed and touch is not None:
                tx, ty = touch
                swipe_start_x, swipe_start_y = tx, ty
                last_activity = now
                # Small delay to ensure stable touch reading
                time.sleep_ms(5)
                # Update coordinates in case of drift
                t = read_touch()
                if t is not None:
                    tx, ty = t
                # Wait for touch release (faster polling for better responsiveness)
                # Keep updating tx, ty to capture the swipe end position!
                while read_touch() is not None:
                    t = read_touch()
                    if t is not None:
                        tx, ty = t
                    time.sleep_ms(10)
                # Handle touch after release
                if current_app == 0: handle_2048_touch(tx, ty)
                elif current_app == 1: handle_battleship_touch(tx, ty)
                elif current_app == 2: handle_books_touch(tx, ty)
                elif current_app == 3: handle_brick_touch(tx, ty)
                elif current_app == 4: handle_calculator_touch(tx, ty)
                elif current_app == 5: handle_checkers_touch(tx, ty)
                elif current_app == 6: handle_chess_touch(tx, ty)
                elif current_app == 7: handle_clock_touch(tx, ty)
                elif current_app == 8: handle_connect4_touch(tx, ty)
                elif current_app == 9: handle_draw_touch(tx, ty)
                elif current_app == 10: handle_flappy_touch(tx, ty)
                elif current_app == 11: handle_life_touch(tx, ty)
                elif current_app == 12: handle_gdash_touch(tx, ty)
                elif current_app == 13: handle_gyro_touch(tx, ty)
                elif current_app == 14: handle_laser_touch(tx, ty)
                elif current_app == 15: handle_mastermind_touch(tx, ty)
                elif current_app == 16: handle_maze_touch(tx, ty)
                elif current_app == 17: handle_minesweeper_touch(tx, ty)
                elif current_app == 18: handle_notes_touch(tx, ty)
                elif current_app == 19: handle_photos_touch(tx, ty)
                elif current_app == 20: handle_pong_touch(tx, ty)
                elif current_app == 21: handle_sliding_touch(tx, ty)
                elif current_app == 22: handle_snake_touch(tx, ty)
                elif current_app == 23: handle_invaders_touch(tx, ty)
                elif current_app == 24: handle_sudoku_touch(tx, ty)
                elif current_app == 25: handle_tictactoe_touch(tx, ty)
                elif current_app == 26: handle_flips_touch(tx, ty)
                elif current_app == 27: handle_wordsearch_touch(tx, ty)
                elif current_app == 28: handle_wordle_touch(tx, ty)
                elif current_app == 29:  # SETTINGS
                    # Settings app touch handling
                    if settings_submenu == -1:
                        y_start = 80
                        row_height = 50
                        items = get_settings_items()
                        if ty < y_start and settings_scroll > 0:
                            settings_scroll = max(0, settings_scroll - SETTINGS_VISIBLE)
                            draw_settings_app()
                        elif ty > y_start + SETTINGS_VISIBLE * row_height and settings_scroll + SETTINGS_VISIBLE < len(items):
                            settings_scroll += SETTINGS_VISIBLE
                            draw_settings_app()
                        else:
                            for i in range(SETTINGS_VISIBLE):
                                vi = settings_scroll + i
                                if vi >= len(items):
                                    break
                                item_top = y_start + i * row_height
                                item_bottom = item_top + row_height
                                if item_top < ty < item_bottom:
                                    ri = SETTINGS_ITEMS.index(items[vi])
                                    settings_submenu = ri
                                    if ri == 0:
                                        draw_battery_settings()
                                    elif ri == 1:
                                        draw_brightness_settings()
                                    elif ri == 2:
                                        draw_volume_settings()
                                    elif ri == 3:
                                        draw_steps_settings()
                                    elif ri == 4:
                                        draw_globe_settings()
                                    elif ri == 5:
                                        draw_app_sort_settings()
                                    elif ri == 6:
                                        stats_submenu = -1
                                        stats_scroll = 0
                                        draw_stats_menu()
                                    elif ri == 7:
                                        draw_time_settings()
                                    elif ri == 8:
                                        draw_about_settings()
                                    break
                    elif settings_submenu == 1:
                        if ty < 180:
                            if brightness_level < 100:
                                brightness_level += 5
                                display.brightness(int(brightness_level * 2.55))
                                draw_brightness_settings()
                        elif ty > 260:
                            if brightness_level > 5:
                                brightness_level -= 5
                                display.brightness(int(brightness_level * 2.55))
                                draw_brightness_settings()
                    elif settings_submenu == 2:
                        # Volume settings
                        if ty < 180:
                            if volume_level < 100:
                                volume_level += 5
                                draw_volume_settings()
                        elif ty > 260:
                            if volume_level > 0:
                                volume_level -= 5
                                draw_volume_settings()
                    elif settings_submenu == 3:
                        # Steps settings - toggle and reset
                        if 100 <= ty <= 160 and 84 <= tx <= 284:  # Toggle button
                            steps_enabled = not steps_enabled
                            save_steps_settings()
                            draw_steps_settings()
                        elif 340 <= ty <= 390 and 114 <= tx <= 254:  # Reset button
                            step_count = 0
                            save_steps_settings()
                            draw_steps_settings()
                    elif settings_submenu == 4:
                        # Globe settings - two buttons
                        if 180 <= ty <= 250:
                            if 25 <= tx <= 175 and globe_animated:
                                globe_animated = False
                                save_globe_setting()
                                draw_globe_settings()
                            elif 193 <= tx <= 343 and not globe_animated:
                                globe_animated = True
                                save_globe_setting()
                                draw_globe_settings()
                    elif settings_submenu == 5:
                        # App sort settings - two buttons
                        if 180 <= ty <= 250:
                            if 25 <= tx <= 175 and app_sort_mode != 0:
                                app_sort_mode = 0
                                save_app_sort()
                                draw_app_sort_settings()
                            elif 193 <= tx <= 343 and app_sort_mode != 1:
                                app_sort_mode = 1
                                save_app_sort()
                                draw_app_sort_settings()
                    elif settings_submenu == 6:
                        if stats_submenu == -1:
                            # Stats scroll navigation (like app menu)
                            y_start = 80
                            row_height = 50
                            visible_count = min(STATS_PER_PAGE, len(STATS_ITEMS) - stats_scroll)
                            # Slightly bigger hitbox: include top 10px of first item and bottom 10px of last item
                            if ty < y_start + 10 and stats_scroll > 0:
                                stats_scroll = max(0, stats_scroll - STATS_PER_PAGE)
                                draw_stats_menu()
                            elif ty > y_start + visible_count * row_height - 10 and stats_scroll + STATS_PER_PAGE < len(STATS_ITEMS):
                                stats_scroll = min(len(STATS_ITEMS) - STATS_PER_PAGE, stats_scroll + STATS_PER_PAGE)
                                draw_stats_menu()
                            else:
                                for vi in range(visible_count):
                                    item_top = y_start + vi * row_height
                                    item_bottom = item_top + row_height
                                    if item_top < ty < item_bottom:
                                        i = stats_scroll + vi
                                        stats_submenu = i
                                        ms_stats_page = 0
                                        sdk_stats_page = 0
                                        pong_stats_page = 0
                                        ttt_stats_page = 0
                                        if i == 0:
                                            draw_2048_stats()
                                        elif i == 1:
                                            draw_bship_stats()
                                        elif i == 2:
                                            draw_brick_stats()
                                        elif i == 3:
                                            draw_chk_stats()
                                        elif i == 4:
                                            draw_chess_stats()
                                        elif i == 5:
                                            draw_c4_stats()
                                        elif i == 6:
                                            draw_flappy_stats()
                                        elif i == 7:
                                            draw_gd_stats()
                                        elif i == 8:
                                            draw_mm_stats()
                                        elif i == 9:
                                            draw_maze_stats()
                                        elif i == 10:
                                            draw_ms_stats()
                                        elif i == 11:
                                            draw_pong_stats()
                                        elif i == 12:
                                            draw_sl_stats()
                                        elif i == 13:
                                            draw_snake_stats()
                                        elif i == 14:
                                            draw_invaders_stats()
                                        elif i == 15:
                                            draw_sudoku_stats()
                                        elif i == 16:
                                            draw_ttt_stats()
                                        elif i == 17:
                                            draw_flips_stats()
                                        elif i == 18:
                                            draw_ws_stats()
                                        elif i == 19:
                                            draw_wrd_stats()
                                        break
                        else:
                            # Stats sub-page pagination
                            if ty > 400:
                                if stats_submenu == 10:
                                    ms_stats_page = 1 - ms_stats_page
                                    draw_ms_stats()
                                elif stats_submenu == 11:
                                    pong_stats_page = 1 - pong_stats_page
                                    draw_pong_stats()
                                elif stats_submenu == 15:
                                    sdk_stats_page = 1 - sdk_stats_page
                                    draw_sudoku_stats()
                                elif stats_submenu == 16:
                                    ttt_stats_page = 1 - ttt_stats_page
                                    draw_ttt_stats()
                                else:
                                    pong_stats_page = 0
                                    ms_stats_page = 0
                                    sdk_stats_page = 0
                                    ttt_stats_page = 0
                                    stats_scroll = 0
                                    stats_submenu = -1
                                    draw_stats_menu()
                            else:
                                pong_stats_page = 0
                                ms_stats_page = 0
                                ttt_stats_page = 0
                                sdk_stats_page = 0
                                stats_scroll = 0
                                stats_submenu = -1
                                draw_stats_menu()
                    elif settings_submenu == 7:
                        # Time settings
                        if 55 <= ty <= 120:
                            if 30 <= tx <= 170:
                                time_set_h = (time_set_h + 1) % 24
                                draw_time_values()
                            elif 198 <= tx <= 338:
                                time_set_m = (time_set_m + 1) % 60
                                draw_time_values()
                        elif 175 <= ty <= 240:
                            if 30 <= tx <= 170:
                                time_set_h = (time_set_h - 1) % 24
                                draw_time_values()
                            elif 198 <= tx <= 338:
                                time_set_m = (time_set_m - 1) % 60
                                draw_time_values()
                        elif 225 <= ty <= 275:
                            if 15 <= tx <= 125:
                                time_set_y = min(2099, time_set_y + 1)
                                draw_time_values()
                            elif 135 <= tx <= 233:
                                time_set_mo = time_set_mo % 12 + 1
                                draw_time_values()
                            elif 243 <= tx <= 353:
                                max_d = days_in_month(time_set_y, time_set_mo)
                                time_set_d = time_set_d % max_d + 1
                                draw_time_values()
                        elif 325 <= ty <= 375:
                            if 15 <= tx <= 125:
                                time_set_y = max(2024, time_set_y - 1)
                                draw_time_values()
                            elif 135 <= tx <= 233:
                                time_set_mo = (time_set_mo - 2) % 12 + 1
                                draw_time_values()
                            elif 243 <= tx <= 353:
                                max_d = days_in_month(time_set_y, time_set_mo)
                                time_set_d = (time_set_d - 2) % max_d + 1
                                draw_time_values()
                        elif 390 <= ty <= 435 and 84 <= tx <= 284:
                            write_rtc(time_set_h, time_set_m)
                            write_date_rtc(time_set_y, time_set_mo, time_set_d)
                            last_time_text = ""
                            settings_submenu = -1
                            draw_settings_app()
                    elif settings_submenu == 8:
                        # About screen
                        if reading_changelog:
                            if tx < 184:
                                # Left half - previous page
                                if changelog_pos > 0:
                                    changelog_pos = changelog_prev_pos(changelog_pos)
                                    cl_next_pos, cl_eof = draw_changelog()
                                else:
                                    # Already at start - go back to about
                                    reading_changelog = False
                                    changelog_pos = 0
                                    draw_about_settings()
                            else:
                                # Right half - next page
                                if not cl_eof:
                                    changelog_pos = cl_next_pos
                                    cl_next_pos, cl_eof = draw_changelog()
                                else:
                                    # At end - go back to about
                                    reading_changelog = False
                                    changelog_pos = 0
                                    draw_about_settings()
                        else:
                            if 400 <= ty <= 440 and 84 <= tx <= 284:
                                reading_changelog = True
                                changelog_pos = 0
                                cl_next_pos, cl_eof = draw_changelog()
                            else:
                                settings_submenu = -1
                                draw_settings_app()
                    else:
                        settings_submenu = -1
                        draw_settings_app()

            # Continuous updates
            if current_app == 29 and settings_submenu == 0:
                update_battery_values()
                time.sleep_ms(500)
            if current_app == 12 and gd_mode == 1: loop_gdash()
            if current_app == 13: loop_gyro()
            if current_app == 3 and brick_mode == 1: loop_brick()
            if current_app == 7: loop_clock()
            if current_app == 11 and life_running: loop_life()
            if current_app == 10 and flappy_running: loop_flappy()
            if current_app == 9: loop_draw()
            if current_app == 11 and not life_running: loop_life_paused()
            if current_app == 14 and laser_on: laser_update_timer()
            if current_app == 16 and mz_mode == 1: mz_draw_timer()
            if current_app == 20 and pong_mode == 1: loop_pong()
            if current_app == 22 and snake_mode == 1: loop_snake()
            if current_app == 17 and ms_mode == 1 and not ms_first_tap: draw_ms_timer()
            if current_app == 21 and sl_mode == 1: sl_draw_status()
            if current_app == 23 and si_mode == 0: loop_invaders()
            if current_app == 24 and sdk_mode == 1: draw_sdk_timer()
            if current_app == 27 and ws_mode == 1: ws_draw_timer()

        if current_screen in (SCREEN_GLOBE, SCREEN_MENU, SCREEN_CATEGORIES):
            hours, minutes, seconds = read_rtc()
            time_text = f"{hours:02d}:{minutes:02d}"
            if time_text != last_time_text:
                if current_screen == SCREEN_GLOBE:
                    scale = 7
                    text_width = len(time_text) * 6 * scale
                    center_x = (368 - text_width) // 2
                    display.fill_rect(center_x - 5, 45, text_width + 10, 60, BLACK)
                    draw_text(display, time_text, center_x, 50, GREY, scale, SEVEN_SEG_FONT)
                elif current_screen in (SCREEN_MENU, SCREEN_CATEGORIES):
                    display.fill_rect(15, 15, 100, 25, BLACK)
                    draw_text(display, time_text, 15, 15, GREY, 3, CODE_FONT)
                last_time_text = time_text
            if current_screen == SCREEN_GLOBE:
                year, month, day = read_date_rtc()
                date_text = f"{year}-{month:02d}-{day:02d}"
                if date_text != last_date_text:
                    scale_date = 4
                    date_width = len(date_text) * 6 * scale_date
                    center_x_date = (368 - date_width) // 2
                    display.fill_rect(center_x_date - 5, 115, date_width + 10, 40, BLACK)
                    draw_text(display, date_text, center_x_date, 120, GREY, scale_date, CODE_FONT)
                    last_date_text = date_text

            # Globe animation
            if globe_animated and current_screen == SCREEN_GLOBE:
                now = time.ticks_ms()
                if time.ticks_diff(now, globe_last_frame_ms) >= 30:
                    globe_frame = (globe_frame + 1) % GLOBE_FRAMES
                    display.jpg(f'globe/GLOBE_{globe_frame+1:03d}.jpg', 68, 175)
                    globe_last_frame_ms = now

            # Step counter - runs on all screens when enabled
            if steps_enabled:
                old_count = step_count
                detect_step()
                if step_count != old_count and current_screen == SCREEN_GLOBE:
                    steps_text = f"{step_count} STEPS"
                    steps_width = len(steps_text) * 6 * 2
                    center_x_steps = (368 - steps_width) // 2
                    display.fill_rect(50, 415, 268, 30, BLACK)
                    draw_text(display, steps_text, center_x_steps, 420, GREEN, 2, CODE_FONT)

        if not (globe_animated and current_screen == SCREEN_GLOBE):
            time.sleep_ms(30)

except KeyboardInterrupt:
    print("Stopped!")
