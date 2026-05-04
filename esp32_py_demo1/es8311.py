# ES8311 Audio Codec Driver - Working config from audio_test v9 C1
# BCLK-derived clock, 32-bit word length, x2 multiplier

class ES8311:
    def __init__(self, i2c):
        self.i2c = i2c

    def _wr(self, reg, val):
        self.i2c.writeto(0x18, bytes([reg, val]))

    def init(self):
        import time
        self._wr(0x44, 0x08)       # I2C noise immunity
        self._wr(0x01, 0x30)       # Initial clocks
        self._wr(0x02, 0x00)
        self._wr(0x03, 0x10)
        self._wr(0x16, 0x24)
        self._wr(0x04, 0x10)
        self._wr(0x05, 0x00)
        self._wr(0x0B, 0x00)
        self._wr(0x0C, 0x00)
        self._wr(0x10, 0x1F)
        self._wr(0x11, 0x7F)
        self._wr(0x00, 0x80)       # Power on, slave mode
        time.sleep_ms(10)
        self._wr(0x01, 0xBF)       # All clocks ON + BCLK source
        self._wr(0x02, 0x08)       # pre_div=1, x2 multiplier
        self._wr(0x03, 0x10)
        self._wr(0x04, 0x20)
        self._wr(0x05, 0x00)
        self._wr(0x06, 0x03)
        self._wr(0x07, 0x00)
        self._wr(0x08, 0xFF)
        self._wr(0x09, 0x00)       # 32-bit word length
        self._wr(0x0A, 0x00)
        self._wr(0x13, 0x10)
        self._wr(0x1B, 0x0A)
        self._wr(0x1C, 0x6A)
        self._wr(0x0D, 0x01)       # Analog power up
        self._wr(0x0E, 0x02)       # DAC ref enable
        self._wr(0x0F, 0x44)       # DAC power enable
        self._wr(0x12, 0x00)
        self._wr(0x32, 0xBF)       # Volume 0dB
        self._wr(0x37, 0x08)       # DAC output enable

    def set_volume(self, level):
        if level <= 0:
            self._wr(0x32, 0xFF)
        elif level >= 100:
            self._wr(0x32, 0x00)
        else:
            self._wr(0x32, int(0xBF * (100 - level) / 100))

    def deinit(self):
        self._wr(0x32, 0xFF)
        self._wr(0x37, 0x00)
        self._wr(0x0F, 0x00)
        self._wr(0x0D, 0x00)
