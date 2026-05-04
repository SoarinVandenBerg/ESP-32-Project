"""
Upload game files to ESP32 via serial connection
Run this script when Thonny file browser doesn't work
"""
import serial
import time
import os

# Configure your COM port here
COM_PORT = "COM3"  # Change this to your ESP32's COM port
BAUD_RATE = 115200

def send_file(ser, local_path, remote_path):
    """Upload a single file to ESP32"""
    print(f"Uploading {local_path} -> {remote_path}...")

    with open(local_path, 'rb') as f:
        content = f.read()

    # Escape content for Python string
    escaped = content.replace(b'\\', b'\\\\').replace(b'"', b'\\"')

    # Create remote file
    cmd = f'f=open("{remote_path}","wb")\r\n'
    ser.write(cmd.encode())
    time.sleep(0.1)

    # Write in chunks
    chunk_size = 256
    for i in range(0, len(escaped), chunk_size):
        chunk = escaped[i:i+chunk_size]
        ser.write(b'f.write(b"' + chunk + b'")\r\n')
        time.sleep(0.05)

    # Close file
    ser.write(b'f.close()\r\n')
    time.sleep(0.1)
    print(f"  ✓ Done")

def main():
    print("ESP32 Game Files Uploader")
    print("=" * 50)

    # Check files exist
    games_dir = "games"
    if not os.path.exists(games_dir):
        print(f"Error: {games_dir} directory not found!")
        return

    game_files = [f for f in os.listdir(games_dir) if f.endswith('.py')]
    print(f"Found {len(game_files)} game files to upload")

    # Connect to ESP32
    print(f"\nConnecting to {COM_PORT}...")
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)

        # Enter REPL
        ser.write(b'\x03')  # Ctrl-C
        time.sleep(0.5)
        ser.write(b'\x03')  # Ctrl-C again
        time.sleep(0.5)

        print("Connected!\n")

        # Upload each game file
        for game_file in sorted(game_files):
            local_path = os.path.join(games_dir, game_file)
            remote_path = f"/games/{game_file}"
            send_file(ser, local_path, remote_path)

        print("\n" + "=" * 50)
        print("All files uploaded successfully!")
        print("Press Ctrl+D in Thonny to reboot the ESP32")

        ser.close()

    except serial.SerialException as e:
        print(f"Error: Could not connect to {COM_PORT}")
        print(f"Details: {e}")
        print("\nMake sure:")
        print("1. ESP32 is connected")
        print("2. Thonny is closed (only one program can use the serial port)")
        print("3. COM port is correct")

if __name__ == "__main__":
    main()
