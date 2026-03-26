import time
import numpy as np
from quanser.hardware import HIL, HILError

# Setup
board_type = "qube_servo3_usb"
board_identifier = "0"

# Channels
encoder_chan = np.array([0], dtype=np.uint32)  # Arm encoder
analog_chan = np.array([0], dtype=np.uint32)   # Motor voltage
# Combined Digital Channels: [Enable, Red, Green, Blue]
digital_chans = np.array([0, 1, 2, 3], dtype=np.uint32)

# State: Enable=1, Red=0, Green=1, Blue=0 (This makes it Green)
# Note: Digital values are integers (0 or 1)
green_state = np.array([1, 0, 1, 0], dtype=np.int32)

# State for shutdown: Enable=0, Red=1, Green=0, Blue=0 (Back to Red)
red_state = np.array([0, 1, 0, 0], dtype=np.int32)

board = HIL()

try:
    board.open(board_type, board_identifier)
    
    # --- CRITICAL STEP: Enable the Motor Amplifier ---
    # Enable motor AND turn LED Green in one command
    board.write_digital(digital_chans, len(digital_chans), green_state)
    print("Amplifier Enabled | LED set to Green")
    
    # Small delay to let the amp kick in
    time.sleep(0.1)
    
    # Set LED to Green to show the program is running
    board.write_other(led_channels, len(led_channels), green_color)
    
    # We'll apply 0.5 Volts (enough to move, but slow enough to be safe)
    voltages = np.array([0.5], dtype=np.float64)
    encoder_buffer = np.zeros(1, dtype=np.int32)

    print("Starting motor... Watch the arm!")
    
    start_time = time.time()
    while time.time() - start_time < 2.0:
        # 1. Write Voltage to Motor
        board.write_analog(analog_chan, len(analog_chan), voltages)
        
        # 2. Read Position
        board.read_encoder(encoder_chan, len(encoder_chan), encoder_buffer)
        
        print(f"Voltage: {voltages[0]}V | Encoder: {encoder_buffer[0]}", end="\r")
        time.sleep(0.01) # 100Hz loop

    # STOP the motor by writing 0V before finishing
    board.write_analog(analog_chan, len(analog_chan), np.zeros(1, dtype=np.float64))
    print("\nMotor stopped.")

except HILError as e:
    print(f"\nHardware Error: {e.get_error_message()}")
finally:
    if board.is_valid():
        # Closing the board automatically zeros outputs for safety
        # Reset: Disable motor and turn LED Red before closing
        board.write_digital(digital_chans, len(digital_chans), red_state)
        board.close()
        print("Board closed safely.")