"""
TCA9554 I2C GPIO Expander Driver for MicroPython
=================================================

This driver controls the TCA9554 8-bit I/O expander used on the
Waveshare ESP32-S3-Touch-AMOLED-1.8 board.

The TCA9554 controls critical functions:
- EXIO_0: Not used (or board-specific)
- EXIO_1: AMOLED display enable (must be HIGH to power display)
- EXIO_2: Touch panel reset (must be HIGH for normal operation)
- EXIO_3-7: Various other functions

I2C Address: 0x20

Registers:
- 0x00: Input port (read-only)
- 0x01: Output port (read/write)
- 0x02: Polarity inversion
- 0x03: Configuration (0=output, 1=input)

Usage:
    from machine import I2C, Pin
    import tca9554
    
    i2c = I2C(0, sda=Pin(6), scl=Pin(7), freq=400000)
    expander = tca9554.TCA9554(i2c)
    
    # Enable AMOLED display
    expander.enable_amoled()
    
    # Or control individual pins
    expander.set_pin(1, True)  # Set EXIO_1 high
"""

class TCA9554:
    """TCA9554 I2C GPIO Expander driver"""
    
    # Default I2C address
    DEFAULT_ADDR = 0x20
    
    # Register addresses
    REG_INPUT = 0x00
    REG_OUTPUT = 0x01
    REG_POLARITY = 0x02
    REG_CONFIG = 0x03
    
    # Pin assignments for Waveshare ESP32-S3-Touch-AMOLED-1.8
    PIN_LCD_RST = 0     # EXIO_0: LCD reset
    PIN_AMOLED_EN = 1   # EXIO_1: AMOLED display enable (DSI_PWR_EN)
    PIN_TP_RST = 2      # EXIO_2: Touch panel reset
    
    def __init__(self, i2c, addr=DEFAULT_ADDR):
        """
        Initialize TCA9554 GPIO expander.
        
        Args:
            i2c: Initialized I2C bus object
            addr: I2C address (default 0x20)
        """
        self.i2c = i2c
        self.addr = addr
        self._output_state = 0x00  # Track current output state
        
        # Verify device is present
        devices = i2c.scan()
        if addr not in devices:
            raise RuntimeError(f"TCA9554 not found at address 0x{addr:02X}. Found: {[hex(d) for d in devices]}")
        
        # Initialize: all pins as output, all low
        self._write_reg(self.REG_CONFIG, 0x00)  # All pins as output
        self._write_reg(self.REG_OUTPUT, 0x00)  # All pins low
    
    def _write_reg(self, reg, value):
        """Write a value to a register."""
        self.i2c.writeto(self.addr, bytes([reg, value]))
    
    def _read_reg(self, reg):
        """Read a value from a register."""
        self.i2c.writeto(self.addr, bytes([reg]))
        return self.i2c.readfrom(self.addr, 1)[0]
    
    def set_pin(self, pin, value):
        """
        Set a single pin high or low.
        
        Args:
            pin: Pin number (0-7)
            value: True for high, False for low
        """
        if not 0 <= pin <= 7:
            raise ValueError("Pin must be 0-7")
        
        if value:
            self._output_state |= (1 << pin)
        else:
            self._output_state &= ~(1 << pin)
        
        self._write_reg(self.REG_OUTPUT, self._output_state)
    
    def get_pin(self, pin):
        """
        Read a pin's input state.
        
        Args:
            pin: Pin number (0-7)
            
        Returns:
            True if high, False if low
        """
        if not 0 <= pin <= 7:
            raise ValueError("Pin must be 0-7")
        
        value = self._read_reg(self.REG_INPUT)
        return bool(value & (1 << pin))
    
    def set_pin_mode(self, pin, is_input):
        """
        Set a pin as input or output.
        
        Args:
            pin: Pin number (0-7)
            is_input: True for input, False for output
        """
        if not 0 <= pin <= 7:
            raise ValueError("Pin must be 0-7")
        
        config = self._read_reg(self.REG_CONFIG)
        if is_input:
            config |= (1 << pin)
        else:
            config &= ~(1 << pin)
        self._write_reg(self.REG_CONFIG, config)
    
    def write_all(self, value):
        """
        Write all 8 output pins at once.
        
        Args:
            value: 8-bit value (bit 0 = pin 0, etc.)
        """
        self._output_state = value & 0xFF
        self._write_reg(self.REG_OUTPUT, self._output_state)
    
    def read_all(self):
        """
        Read all 8 input pins at once.
        
        Returns:
            8-bit value representing all pin states
        """
        return self._read_reg(self.REG_INPUT)
    
    def enable_amoled(self):
        """
        Enable the AMOLED display with proper reset sequence.
        1. Power on with LCD reset held LOW
        2. Release LCD reset
        3. Release touch reset
        """
        import time
        
        # Power on, but hold LCD reset LOW
        self._output_state = (1 << self.PIN_AMOLED_EN)  # Only power enable
        self._write_reg(self.REG_OUTPUT, self._output_state)
        time.sleep_ms(50)
        
        # Release LCD reset and touch reset
        self._output_state |= (1 << self.PIN_LCD_RST) | (1 << self.PIN_TP_RST)
        self._write_reg(self.REG_OUTPUT, self._output_state)
        time.sleep_ms(150)
    
    def disable_amoled(self):
        """
        Disable the AMOLED display.
        Sets EXIO_1 low to power off the display.
        """
        self._output_state &= ~(1 << self.PIN_AMOLED_EN)
        self._write_reg(self.REG_OUTPUT, self._output_state)
    
    def reset_touch(self):
        """
        Reset the touch panel.
        Pulses EXIO_2 low then high.
        """
        import time
        self.set_pin(self.PIN_TP_RST, False)
        time.sleep_ms(10)
        self.set_pin(self.PIN_TP_RST, True)
        time.sleep_ms(50)


# Convenience class for individual pin control (compatible with dobodu's approach)
class TCA9554Pin:
    """
    Wrapper to make a TCA9554 pin act like a machine.Pin object.
    
    Usage:
        expander = TCA9554(i2c)
        amoled_en = TCA9554Pin(expander, 1)
        amoled_en.value(1)  # Enable AMOLED
    """
    
    def __init__(self, expander, pin, mode='out'):
        """
        Create a pin wrapper.
        
        Args:
            expander: TCA9554 instance
            pin: Pin number (0-7)
            mode: 'in' for input, 'out' for output
        """
        self.expander = expander
        self.pin = pin
        self.expander.set_pin_mode(pin, mode == 'in')
    
    def value(self, val=None):
        """
        Get or set the pin value.
        
        Args:
            val: If provided, set the pin to this value (0 or 1)
            
        Returns:
            Current pin value if val is None
        """
        if val is None:
            return 1 if self.expander.get_pin(self.pin) else 0
        else:
            self.expander.set_pin(self.pin, bool(val))
    
    def on(self):
        """Set pin high."""
        self.value(1)
    
    def off(self):
        """Set pin low."""
        self.value(0)
    
    def __call__(self, val=None):
        """Allow pin(1) or pin() syntax."""
        return self.value(val)
