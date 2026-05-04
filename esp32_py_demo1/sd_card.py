# SD Card driver for ESP32-S3-Touch-AMOLED-1.8
# Handles the TCA9554 GPIO expander for CS pin

from machine import SPI, Pin, SoftI2C
import os

# TCA9554 I2C address
TCA9554_ADDR = 0x20
TCA9554_OUTPUT_REG = 0x01

class TCA9554Pin:
    """Fake Pin class that controls EXIO7 via TCA9554 for SD card CS"""
    def __init__(self, i2c, bit=7):
        self.i2c = i2c
        self.bit = bit
        self._mask = 1 << bit
        # Read current output state
        self.i2c.writeto(TCA9554_ADDR, bytes([TCA9554_OUTPUT_REG]))
        self._state = self.i2c.readfrom(TCA9554_ADDR, 1)[0]

    def __call__(self, value=None):
        if value is None:
            return (self._state >> self.bit) & 1
        self.value(value)

    def value(self, val=None):
        if val is None:
            return (self._state >> self.bit) & 1
        if val:
            self._state |= self._mask
        else:
            self._state &= ~self._mask
        self.i2c.writeto(TCA9554_ADDR, bytes([TCA9554_OUTPUT_REG, self._state]))

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

class SDCard:
    """SD Card interface using SPI with TCA9554-controlled CS"""
    def __init__(self, i2c=None):
        # Use provided i2c or create new one
        if i2c is None:
            self.i2c = SoftI2C(sda=Pin(15), scl=Pin(14), freq=400000)
        else:
            self.i2c = i2c

        self.mounted = False
        self.sd = None

    def mount(self, path='/sd'):
        """Mount the SD card to the specified path"""
        if self.mounted:
            return True

        try:
            # Import sdcard module
            import sdcard

            # Create SPI for SD card (different from display SPI)
            spi = SPI(1, baudrate=1000000, polarity=0, phase=0,
                     sck=Pin(2), mosi=Pin(1), miso=Pin(3))

            # Create fake CS pin using TCA9554
            cs = TCA9554Pin(self.i2c, bit=7)
            cs.value(1)  # Deselect initially

            # Create SD card object
            self.sd = sdcard.SDCard(spi, cs)

            # Mount filesystem
            os.mount(self.sd, path)
            self.mounted = True
            self.path = path
            print(f"SD card mounted at {path}")

            # Increase SPI speed after init
            spi = SPI(1, baudrate=20000000, polarity=0, phase=0,
                     sck=Pin(2), mosi=Pin(1), miso=Pin(3))

            return True

        except Exception as e:
            print(f"SD card mount failed: {e}")
            return False

    def unmount(self):
        """Unmount the SD card"""
        if self.mounted:
            try:
                os.umount(self.path)
                self.mounted = False
                print("SD card unmounted")
            except:
                pass

    def list_files(self, path=None, ext=None):
        """List files in directory, optionally filter by extension"""
        if not self.mounted:
            return []

        if path is None:
            path = self.path

        try:
            files = os.listdir(path)
            if ext:
                files = [f for f in files if f.lower().endswith(ext.lower())]
            return sorted(files)
        except:
            return []

    def list_books(self):
        """List all .txt files on the SD card"""
        return self.list_files(ext='.txt')


# Quick test function
def test_sd():
    sd = SDCard()
    if sd.mount():
        print("Files:", sd.list_files())
        print("Books:", sd.list_books())
        sd.unmount()
    else:
        print("Failed to mount SD card")
