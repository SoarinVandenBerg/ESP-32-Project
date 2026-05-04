"""
boot.py - Automatic initialization for Waveshare ESP32-S3-Touch-AMOLED-1.8
==========================================================================

This boot script initializes the board hardware at startup, including:
1. I2C bus
2. TCA9554 GPIO expander
3. AMOLED display power enable

Place this file in the root of your MicroPython filesystem to have
the board automatically initialized on boot.

After boot, you can immediately use the display:

    import waveshare_amoled_18 as board
    display = board.create_display()
    display.fill(board.RED)
"""

import gc

# Minimal boot - just enable the display hardware
# This doesn't import the full amoled module to keep boot fast

def _boot_init():
    """Minimal initialization to enable display hardware."""
    from machine import SoftI2C, Pin
    import time
    
    # I2C pins for Waveshare ESP32-S3-Touch-AMOLED-1.8
    I2C_SDA = 15
    I2C_SCL = 14
    TCA9554_ADDR = 0x20
    
    try:
        # Initialize I2C
        i2c = SoftI2C(sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400000)
        
        # Check if TCA9554 is present
        devices = i2c.scan()
        if TCA9554_ADDR not in devices:
            print(f"Warning: TCA9554 not found at 0x{TCA9554_ADDR:02X}")
            print(f"Found devices: {[hex(d) for d in devices]}")
            return
        
        # Configure TCA9554: all pins as output
        i2c.writeto(TCA9554_ADDR, bytes([0x03, 0x00]))  # Config register: all output
        
        # Reset sequence:
        # EXIO0 = LCD reset, EXIO1 = AMOLED power, EXIO2 = Touch reset
        # Step 1: Power on, hold reset LOW
        i2c.writeto(TCA9554_ADDR, bytes([0x01, 0x02]))  # Only EXIO1 (power) high
        time.sleep_ms(50)
        
        # Step 2: Release all resets
        i2c.writeto(TCA9554_ADDR, bytes([0x01, 0x07]))  # EXIO0, EXIO1, EXIO2 all high
        time.sleep_ms(150)
        
        print("Waveshare AMOLED 1.8: Display power enabled")
        
    except Exception as e:
        print(f"Boot init error: {e}")

# Run initialization
_boot_init()

# Clean up
gc.collect()
