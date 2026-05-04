"""
Waveshare ESP32-S3-Touch-AMOLED-1.8 Board Configuration
========================================================

This module provides pin definitions and initialization routines for the
Waveshare ESP32-S3-Touch-AMOLED-1.8 development board.

Hardware Specifications:
- Display: 1.8" AMOLED, 368x448 pixels, SH8601 driver (QSPI)
- Touch: FT3168 capacitive touch controller (I2C @ 0x38)
- IMU: QMI8658 6-axis sensor (I2C @ 0x6B)
- RTC: PCF85063 (I2C @ 0x51)
- PMU: AXP2101 power management (I2C @ 0x34)
- GPIO Expander: TCA9554 (I2C @ 0x20)

CRITICAL: The TCA9554 GPIO expander controls the AMOLED power enable.
You MUST initialize it and enable EXIO_1 before the display will work!

Usage:
    import waveshare_amoled_18 as board
    
    # Initialize I2C and GPIO expander (required before display!)
    board.init()
    
    # Now you can use the display
    import amoled
    display = board.create_display()
    display.fill(board.RED)
    display.text(board.font, "Hello!", 10, 10, board.WHITE)

Author: Generated for Waveshare ESP32-S3-Touch-AMOLED-1.8
License: MIT
"""

from machine import Pin, SPI, SoftI2C
import time

# =============================================================================
# PIN DEFINITIONS
# =============================================================================

# I2C Bus (shared by all I2C devices)
I2C_SDA = 15
I2C_SCL = 14
I2C_FREQ = 400000

# I2C Device Addresses
ADDR_TCA9554 = 0x20    # GPIO Expander (controls AMOLED enable)
ADDR_AXP2101 = 0x34    # Power Management IC
ADDR_FT3168 = 0x38     # Touch Controller
ADDR_PCF85063 = 0x51   # RTC
ADDR_QMI8658 = 0x6B    # 6-axis IMU

# Expected I2C devices (for scan verification)
EXPECTED_I2C_DEVICES = [ADDR_TCA9554, ADDR_AXP2101, ADDR_FT3168, ADDR_PCF85063, ADDR_QMI8658]

# QSPI Display Pins (SH8601 driver)
LCD_CS = 12
LCD_SCLK = 11
LCD_D0 = 4     # QSPI Data 0
LCD_D1 = 5     # QSPI Data 1
LCD_D2 = 6     # QSPI Data 2
LCD_D3 = 7     # QSPI Data 3
# Note: LCD_RST is controlled via TCA9554 EXIO0, not a direct GPIO

# Display Parameters
LCD_WIDTH = 368
LCD_HEIGHT = 448
LCD_TYPE = 2   # SH8601 driver type for dobodu's amoled module

# Touch Interrupt
TOUCH_INT = 21

# IMU Interrupts
IMU_INT1 = 4
IMU_INT2 = 5

# GPIO Expander Pin Assignments (accent via TCA9554 I2C, not direct GPIO!)
EXIO_LCD_RST = 0      # Bit 0: LCD reset
EXIO_AMOLED_EN = 1    # Bit 1: AMOLED display enable (DSI_PWR_EN)
EXIO_TP_RST = 2       # Bit 2: Touch panel reset

# SD Card (SD_MMC mode)
SD_MMC_CLK = 38
SD_MMC_CMD = 39
SD_MMC_D0 = 40

# Audio I2S (ES8311 codec)
AUDIO_I2S_MCLK = 16
AUDIO_I2S_BCK = 9
AUDIO_I2S_WS = 45
AUDIO_I2S_DOUT = 8
AUDIO_I2S_DIN = 10
AUDIO_PA_CTRL = 46   # Speaker amplifier enable

# Microphone PDM
MIC_CLK = 48
MIC_DATA = 47

# SPI Configuration for Display
SPI_PORT = 2
SPI_BAUD = 80_000_000
SPI_POLAR = False
SPI_PHASE = False

# =============================================================================
# COLORS (RGB565 format)
# =============================================================================

BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
CYAN = 0x07FF
MAGENTA = 0xF81F
YELLOW = 0xFFE0

# =============================================================================
# GLOBAL STATE
# =============================================================================

_i2c = None
_expander = None
_display = None
_initialized = False

# =============================================================================
# INITIALIZATION FUNCTIONS
# =============================================================================

def init_i2c():
    """
    Initialize the I2C bus.
    
    Returns:
        I2C object
    """
    global _i2c
    if _i2c is None:
        from machine import SoftI2C
        _i2c = SoftI2C(sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=I2C_FREQ)
    return _i2c


def scan_i2c():
    """
    Scan the I2C bus and print found devices.
    
    Returns:
        List of found I2C addresses
    """
    i2c = init_i2c()
    devices = i2c.scan()
    
    print(f"I2C scan found {len(devices)} device(s):")
    
    known_devices = {
        ADDR_TCA9554: "TCA9554 GPIO Expander",
        ADDR_AXP2101: "AXP2101 Power Management",
        ADDR_FT3168: "FT3168 Touch Controller",
        ADDR_PCF85063: "PCF85063 RTC",
        ADDR_QMI8658: "QMI8658 IMU",
    }
    
    for addr in devices:
        name = known_devices.get(addr, "Unknown")
        print(f"  0x{addr:02X} ({addr:3d}) - {name}")
    
    # Check for missing devices
    missing = [addr for addr in EXPECTED_I2C_DEVICES if addr not in devices]
    if missing:
        print(f"\nWarning: Missing expected devices: {[hex(a) for a in missing]}")
    
    return devices


def init_expander():
    """
    Initialize the TCA9554 GPIO expander.
    
    Returns:
        TCA9554 object
    """
    global _expander
    if _expander is None:
        from tca9554 import TCA9554
        i2c = init_i2c()
        _expander = TCA9554(i2c, ADDR_TCA9554)
    return _expander


def enable_display():
    """
    Enable the AMOLED display via GPIO expander.
    This MUST be called before initializing the display!
    """
    expander = init_expander()
    expander.enable_amoled()
    time.sleep_ms(100)  # Wait for display to power up
    print("AMOLED display enabled via TCA9554")


def disable_display():
    """
    Disable the AMOLED display to save power.
    """
    expander = init_expander()
    expander.disable_amoled()
    print("AMOLED display disabled")


def init(verbose=True):
    """
    Full board initialization sequence.
    
    This performs:
    1. I2C bus initialization
    2. I2C device scan (optional)
    3. GPIO expander initialization
    4. AMOLED display power enable
    
    Args:
        verbose: Print status messages
        
    Returns:
        True if successful
    """
    global _initialized
    
    if _initialized:
        if verbose:
            print("Board already initialized")
        return True
    
    if verbose:
        print("Initializing Waveshare ESP32-S3-Touch-AMOLED-1.8...")
    
    # Initialize I2C
    init_i2c()
    if verbose:
        print(f"  I2C initialized on SDA={I2C_SDA}, SCL={I2C_SCL}")
    
    # Scan I2C bus
    if verbose:
        scan_i2c()
    
    # Initialize GPIO expander and enable display
    enable_display()
    
    _initialized = True
    if verbose:
        print("Board initialization complete!")
        print(f"\nDisplay: {LCD_WIDTH}x{LCD_HEIGHT} SH8601 AMOLED (type={LCD_TYPE})")
    
    return True


def create_display(auto_refresh=True):
    """
    Create and initialize the AMOLED display.
    
    IMPORTANT: Call init() first to enable display power!
    
    Args:
        auto_refresh: Enable automatic display refresh
        
    Returns:
        AMOLED display object
    """
    global _display
    
    if not _initialized:
        print("Warning: Board not initialized. Calling init()...")
        init()
    
    if _display is not None:
        return _display
    
    import amoled
    
    # Create SPI bus
    spi = SPI(SPI_PORT, 
              baudrate=SPI_BAUD, 
              sck=Pin(LCD_SCLK), 
              mosi=None, 
              miso=None, 
              polarity=SPI_POLAR, 
              phase=SPI_PHASE)
    
    # Create QSPI panel
    panel = amoled.QSPIPanel(
        spi=spi,
        data=(Pin(LCD_D0), Pin(LCD_D1), Pin(LCD_D2), Pin(LCD_D3)),
        dc=Pin(LCD_D1),
        cs=Pin(LCD_CS),
        pclk=SPI_BAUD,
        width=LCD_WIDTH,
        height=LCD_HEIGHT
    )
    
    # Create AMOLED display
    # type=2 is SH8601 driver
    # Note: reset is handled by TCA9554, not passed here
    _display = amoled.AMOLED(
        panel,
        type=LCD_TYPE,
        bpp=16,
        auto_refresh=auto_refresh
    )
    
    # Initialize display
    _display.init()
    _display.brightness(255)
    
    print(f"Display created: {LCD_WIDTH}x{LCD_HEIGHT}")
    return _display


def get_display():
    """
    Get the current display object, creating if necessary.
    """
    global _display
    if _display is None:
        return create_display()
    return _display


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def test_display():
    """
    Test the display with some basic graphics.
    """
    display = create_display()
    
    print("Testing display...")
    
    # Fill with colors
    display.fill(RED)
    time.sleep_ms(500)
    
    display.fill(GREEN)
    time.sleep_ms(500)
    
    display.fill(BLUE)
    time.sleep_ms(500)
    
    display.fill(BLACK)
    
    # Draw some shapes
    display.rect(10, 10, 100, 100, WHITE)
    display.fill_rect(120, 10, 100, 100, CYAN)
    display.circle(60, 200, 50, YELLOW)
    display.fill_circle(180, 200, 50, MAGENTA)
    
    # Draw text (requires font module)
    try:
        import vga1_16x32 as font
        display.text(font, "Waveshare", 10, 300, WHITE, BLACK)
        display.text(font, "AMOLED 1.8", 10, 340, GREEN, BLACK)
        display.text(font, "368x448", 10, 380, CYAN, BLACK)
    except ImportError:
        print("Font module not found, skipping text test")
    
    print("Display test complete!")


def print_info():
    """
    Print board information.
    """
    print("=" * 50)
    print("Waveshare ESP32-S3-Touch-AMOLED-1.8")
    print("=" * 50)
    print(f"Display: {LCD_WIDTH}x{LCD_HEIGHT} SH8601 AMOLED")
    print(f"I2C: SDA={I2C_SDA}, SCL={I2C_SCL}")
    print(f"QSPI: CS={LCD_CS}, CLK={LCD_SCLK}, D0-D3={LCD_D0}-{LCD_D3}")
    print()
    print("I2C Devices:")
    print(f"  TCA9554 GPIO Expander: 0x{ADDR_TCA9554:02X}")
    print(f"  AXP2101 PMU:           0x{ADDR_AXP2101:02X}")
    print(f"  FT3168 Touch:          0x{ADDR_FT3168:02X}")
    print(f"  PCF85063 RTC:          0x{ADDR_PCF85063:02X}")
    print(f"  QMI8658 IMU:           0x{ADDR_QMI8658:02X}")
    print("=" * 50)


# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

if __name__ == "__main__":
    print_info()
    print()
    init()
    test_display()
