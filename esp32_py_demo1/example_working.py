"""
Working Example for Waveshare ESP32-S3-Touch-AMOLED-1.8
========================================================

This is the CONFIRMED WORKING configuration with correct pin mappings.

Hardware verified: January 2026
Firmware: dobodu AMOLED MicroPython (reports as LILYGO T4-S3)

Correct Pin Mapping:
--------------------
I2C:
  - SDA: GPIO 15
  - SCL: GPIO 14

QSPI Display:
  - CLK:  GPIO 11
  - CS:   GPIO 12
  - D0:   GPIO 4
  - D1:   GPIO 5
  - D2:   GPIO 6
  - D3:   GPIO 7

TCA9554 GPIO Expander (I2C addr 0x20):
  - EXIO0: LCD Reset
  - EXIO1: AMOLED Power Enable
  - EXIO2: Touch Panel Reset

I2C Devices:
  - 0x20: TCA9554 GPIO Expander
  - 0x34: AXP2101 PMU
  - 0x38: FT3168 Touch Controller (appears after TCA9554 init)
  - 0x51: PCF85063 RTC
  - 0x6B: QMI8658 IMU
"""

from machine import SoftI2C, Pin, SPI
import time

# ============ CORRECT PIN DEFINITIONS ============
# I2C Bus
I2C_SDA = 15
I2C_SCL = 14

# QSPI Display
QSPI_CLK = 11
QSPI_CS = 12
QSPI_D0 = 4
QSPI_D1 = 5
QSPI_D2 = 6
QSPI_D3 = 7

# TCA9554
TCA9554_ADDR = 0x20
EXIO_LCD_RST = 0
EXIO_AMOLED_EN = 1
EXIO_TP_RST = 2

# Display
LCD_WIDTH = 368
LCD_HEIGHT = 448


def init_hardware():
    """Initialize I2C and TCA9554 with proper reset sequence."""
    print("Initializing hardware...")
    
    # Initialize I2C
    i2c = SoftI2C(sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400000)
    
    # Scan for devices
    devices = i2c.scan()
    print(f"I2C devices found: {[hex(d) for d in devices]}")
    
    if TCA9554_ADDR not in devices:
        raise RuntimeError("TCA9554 not found!")
    
    # Configure TCA9554: all pins as output
    i2c.writeto(TCA9554_ADDR, bytes([0x03, 0x00]))
    
    # Reset sequence:
    # Step 1: Power on, hold LCD reset LOW
    print("Power on, reset LOW...")
    i2c.writeto(TCA9554_ADDR, bytes([0x01, 0x02]))  # Only EXIO1 high
    time.sleep_ms(50)
    
    # Step 2: Release all resets
    print("Release reset...")
    i2c.writeto(TCA9554_ADDR, bytes([0x01, 0x07]))  # EXIO0, EXIO1, EXIO2 all high
    time.sleep_ms(150)
    
    print("TCA9554 configured")
    
    # Re-scan to see touch controller
    devices = i2c.scan()
    print(f"I2C devices after init: {[hex(d) for d in devices]}")
    
    return i2c


def init_display():
    """Initialize the AMOLED display."""
    import amoled
    
    print("Initializing display...")
    
    # Create SPI bus
    spi = SPI(2, baudrate=80_000_000, sck=Pin(QSPI_CLK), mosi=None, miso=None)
    
    # Create QSPI panel
    panel = amoled.QSPIPanel(
        spi=spi,
        data=(Pin(QSPI_D0), Pin(QSPI_D1), Pin(QSPI_D2), Pin(QSPI_D3)),
        dc=Pin(QSPI_D1),
        cs=Pin(QSPI_CS),
        pclk=80_000_000,
        width=LCD_WIDTH,
        height=LCD_HEIGHT
    )
    
    # Create AMOLED display (type=2 for SH8601)
    display = amoled.AMOLED(panel, type=2, bpp=16, auto_refresh=True)
    
    # Initialize
    display.init()
    display.brightness(255)
    
    print(f"Display ready: {LCD_WIDTH}x{LCD_HEIGHT}")
    return display


def color_test(display):
    """Test display with color fills."""
    import amoled
    
    colors = [
        (amoled.RED, "RED"),
        (amoled.GREEN, "GREEN"),
        (amoled.BLUE, "BLUE"),
        (amoled.WHITE, "WHITE"),
        (amoled.BLACK, "BLACK"),
    ]
    
    for color, name in colors:
        print(f"Filling {name}...")
        display.fill(color)
        time.sleep(1)


def gradient_test(display):
    """Draw a gradient pattern."""
    print("Drawing gradient...")
    
    for y in range(LCD_HEIGHT):
        # Create RGB565 color that varies with Y
        r = (y * 31) // LCD_HEIGHT
        g = ((LCD_HEIGHT - y) * 63) // LCD_HEIGHT
        b = 15
        color = (r << 11) | (g << 5) | b
        display.hline(0, y, LCD_WIDTH, color)


def main():
    """Main entry point."""
    print("\n" + "="*50)
    print("Waveshare ESP32-S3-Touch-AMOLED-1.8 Test")
    print("="*50 + "\n")
    
    # Initialize hardware
    i2c = init_hardware()
    
    # Initialize display
    display = init_display()
    
    # Run tests
    print("\nRunning color test...")
    color_test(display)
    
    print("\nRunning gradient test...")
    gradient_test(display)
    
    print("\n" + "="*50)
    print("Test complete!")
    print("="*50)
    
    return display, i2c


if __name__ == "__main__":
    display, i2c = main()
