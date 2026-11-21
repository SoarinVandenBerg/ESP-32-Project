================================================================
  ESP32-S3 SMARTWATCH - SETUP GUIDE FROM SCRATCH
================================================================

This guide takes you from a blank/new Waveshare ESP32-S3-Touch-AMOLED-1.8
board to a fully running smartwatch using these backup files.

Estimated time: 30-60 minutes (mostly waiting on flash)

----------------------------------------------------------------
  WHAT YOU NEED
----------------------------------------------------------------

HARDWARE:
  - Waveshare ESP32-S3-Touch-AMOLED-1.8 board (368x448 AMOLED)
  - USB-C cable (data, not just power)
  - Windows / Mac / Linux PC
  - Optional: microSD card (for books/photos apps)

SOFTWARE TO INSTALL:
  1. Python 3 (https://www.python.org/downloads/)
  2. Thonny IDE (https://thonny.org)
  3. esptool (installed via pip - step below)

FILES TO DOWNLOAD:
  1. dobodu's AMOLED MicroPython firmware (.bin file)
     URL: https://github.com/dobodu/Lilygo_Waveshare_Amoled_Micropython
     Download the firmware .bin for ESP32-S3 AMOLED 1.8"

  2. This backup folder (you have it: ESP-32 BACKUP)

----------------------------------------------------------------
  STEP 1 - INSTALL PYTHON & ESPTOOL
----------------------------------------------------------------

1. Install Python 3 from python.org. During install, CHECK
   "Add Python to PATH".

2. Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

       pip install esptool

3. Verify it works:

       esptool --version

   Should print a version number (e.g. "esptool 4.x.x").

----------------------------------------------------------------
  STEP 2 - INSTALL THONNY
----------------------------------------------------------------

1. Download Thonny from https://thonny.org and install it.

2. Open Thonny.

3. Go to: Tools -> Options -> Interpreter
       Set Interpreter to: "MicroPython (ESP32)"
       (Don't pick a port yet - the device has no firmware.)

4. Click OK. Close Thonny for now.

----------------------------------------------------------------
  STEP 3 - PLUG IN THE ESP32 AND FIND ITS COM PORT
----------------------------------------------------------------

1. Plug the ESP32-S3 board into your PC via USB-C.

2. WINDOWS: Open Device Manager -> Ports (COM & LPT)
       Look for something like "USB Serial Device (COM5)" or
       "CP210x USB to UART (COM7)". Note the COM number.

   MAC: In Terminal run:  ls /dev/cu.*
       Look for /dev/cu.usbserial-XXXX or similar.

   LINUX: ls /dev/ttyUSB* or /dev/ttyACM*

3. If no port shows up, you may need a USB-to-serial driver:
       CP210x: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
       CH340:  https://www.wch-ic.com/downloads/CH341SER_EXE.html

----------------------------------------------------------------
  STEP 4 - WIPE / ERASE THE ESP32
----------------------------------------------------------------

This deletes EVERYTHING on the chip - old firmware, files, etc.
Replace COMx with your actual port (e.g. COM5).

In Command Prompt / Terminal:

       esptool --chip esp32s3 --port COMx erase_flash

You should see:
       "Chip erase completed successfully"

If you get "Failed to connect", try:
   - Hold the BOOT button on the board, then plug in USB.
   - Or press RESET while running the command.

----------------------------------------------------------------
  STEP 5 - FLASH THE MICROPYTHON FIRMWARE
----------------------------------------------------------------

Put the dobodu firmware .bin file somewhere easy (e.g. Desktop).
Replace the path and COM port:

       esptool --chip esp32s3 --port COMx write_flash 0 firmware.bin

This takes ~1-2 minutes. You'll see progress percentage. When done:
       "Hash of data verified."
       "Hard resetting via RTS pin..."

The display might still be black - that's normal. The firmware is
flashed but boot.py hasn't initialized the screen yet.

----------------------------------------------------------------
  STEP 6 - CONNECT THONNY TO THE BOARD
----------------------------------------------------------------

1. Open Thonny.

2. Tools -> Options -> Interpreter
       Interpreter: MicroPython (ESP32)
       Port: Select your COM port
       Click OK.

3. The bottom panel should show:
       "MicroPython v1.xx ... ESP32-S3"
       ">>>"

4. If you see ">>>", you're talking to the board! Try typing:

       print("hello")

   It should print "hello".

----------------------------------------------------------------
  STEP 7 - UPLOAD ALL THE FILES
----------------------------------------------------------------

Thonny has a Files panel. If you don't see it:
       View -> Files

You'll see TWO sections:
       "This computer"  (top)
       "MicroPython device"  (bottom)

A) UPLOAD ROOT FILES:

   In "This computer", navigate to:  ESP-32 BACKUP\esp32_py_demo1\

   Right-click each of these files -> "Upload to /"
       boot.py
       main.py
       tca9554.py
       waveshare_amoled_18.py
       sdcard.py
       sd_card.py
       es8311.py
       wordle_words.txt
       example_working.py        (optional, for testing)

B) UPLOAD THE GAMES FOLDER:

   1. In the "MicroPython device" panel, right-click -> New folder
       Name it:  games

   2. Double-click into the new "games" folder.

   3. Back in "This computer", navigate to:
       ESP-32 BACKUP\esp32_py_demo1\games\

   4. Select ALL files in that folder (Ctrl+A), right-click ->
      "Upload to /games"

   This uploads ~28 game_*.py files. Takes a couple minutes.

C) UPLOAD THE GLOBE IMAGE:

   1. Go up to root on the device (click ".." in device panel).

   2. In "This computer", navigate to:  ESP-32 BACKUP\
       Right-click GLOBE_1.jpg -> "Upload to /"

D) (Optional) UPLOAD GLOBE ANIMATION FRAMES:

   If the backup includes a "globe" folder with frame images:
   1. Make a "globe" folder on the device (same way as step B1).
   2. Upload all frames from ESP-32 BACKUP\globe\ into it.

----------------------------------------------------------------
  STEP 8 - REBOOT AND ENJOY
----------------------------------------------------------------

1. In Thonny, press Ctrl+D (soft reset) OR unplug/replug the USB.

2. boot.py runs first - initializes the display power.

3. main.py runs next - shows the watch face.

You should see:
   - Globe screen with time and date
   - Tap = goes to menu
   - Hold 3 seconds in any app = exit back to menu
   - Swipe in 2048, etc.

----------------------------------------------------------------
  TROUBLESHOOTING
----------------------------------------------------------------

PROBLEM: Display stays black after boot.
  - boot.py didn't run, or TCA9554 init failed.
  - Check Thonny REPL for error messages.
  - Try running example_working.py manually (F5 in Thonny).

PROBLEM: "ImportError: no module named 'amoled'"
  - Wrong firmware. You need dobodu's AMOLED firmware specifically,
    NOT the standard MicroPython firmware from micropython.org.
  - Erase flash (step 4) and re-flash with the correct .bin.

PROBLEM: Touch doesn't respond.
  - TCA9554 EXIO2 reset wasn't released.
  - Check that boot.py uploaded correctly.

PROBLEM: I2C scan returns empty list [].
  - Code is using GPIO 6/7 for I2C (WRONG - those are display pins!).
  - Make sure tca9554.py and boot.py use SoftI2C with GPIO 15/14.

PROBLEM: Some games crash with "memory allocation failed".
  - Soft reset (Ctrl+D in Thonny REPL) frees memory.
  - This is normal for MicroPython on ESP32.

PROBLEM: Stats / high scores reset every reboot.
  - The board needs to be able to write to flash.
  - Normal during development - they're saved to all_stats.txt.

----------------------------------------------------------------
  HARDWARE PIN REFERENCE (for your sanity)
----------------------------------------------------------------

I2C BUS (use SoftI2C, NOT hardware I2C):
   SDA: GPIO 15  (NOT 6!)
   SCL: GPIO 14  (NOT 7!)

QSPI DISPLAY:
   CLK: 11, CS: 12, D0-D3: 4, 5, 6, 7

I2C DEVICES:
   0x20  TCA9554 GPIO expander (display power, resets)
   0x34  AXP2101 PMU (battery)
   0x38  FT3168 touch
   0x51  PCF85063 RTC
   0x6B  QMI8658 IMU (accelerometer / gyro)

WARNING: Online tutorials and Waveshare's wiki sometimes show
WRONG pin mappings. Trust the schematic, not blog posts:
https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-1.8/ESP32-S3-Touch-AMOLED-1.8.pdf

----------------------------------------------------------------
  WHAT'S IN THIS BACKUP
----------------------------------------------------------------

esp-32 project GITHUB\
  README-SETUP.txt           - This file (setup guide)
  GLOBE_1.jpg                - Globe image for watch face
  globe\                     - Globe animation frames
  convert_music.py           - PC tool for converting audio files
  esp32_py_demo1\
    boot.py                  - Auto-runs on power up (display init)
    main.py                  - The smartwatch app (~5000 lines)
    tca9554.py               - GPIO expander driver
    waveshare_amoled_18.py   - Display init helpers
    sdcard.py / sd_card.py   - SD card support
    es8311.py                - Audio codec driver
    wordle_words.txt         - Word list for Wordle game
    example_working.py       - Hardware test - run this to verify
    games\                   - All ~28 game files
      game_2048.py, game_chess.py, game_pong.py, etc.

----------------------------------------------------------------
  CONTACT / NOTES
----------------------------------------------------------------

Backup snapshot date: March 26, 2026.

Newer versions may exist - this backup is a stable snapshot.
Apps included: 2048, Battleship, Books, Brick Breaker, Calculator,
Checkers, Chess, Clock, Connect Four, Draw, Flappy Bird, Game of
Life, Geometry Dash, Gyro Level, Laser, Mastermind, Maze,
Minesweeper, Notes, Photos, Pong, Sliding Puzzle, Snake, Space
Invaders, Sudoku, Tic-Tac-Toe, Unfair Flips, Word Search, Wordle,
Settings.

Have fun!

----------------------------------------------------------------
These instructions were made by Claude Code :)
----------------------------------------------------------------
