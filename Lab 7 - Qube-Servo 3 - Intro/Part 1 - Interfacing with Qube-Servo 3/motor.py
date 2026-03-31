import time
import numpy as np
from quanser.hardware import HIL, HILError

# Hardware configuration
board_type = "qube_servo3_usb"
board_identifier = "0"

# Minimal Channels
encoder_chan = np.array([0], dtype=np.uint32)
motor_chan = np.array([0], dtype=np.uint32)
enable_chan = np.array([0], dtype=np.uint32)

board = HIL()

try:
    board.open(board_type, board_identifier)
    
    # 1. Enable the motor amplifier
    board.write_digital(enable_chan, 1, np.array([1], dtype=np.int32))
    
    print("Motor active. Reading encoder for 3 seconds...")
    
    start_time = time.time()
    while time.time() - start_time < 3.0:
        # 2. Command 0.5V to the motor
        # Using [0.5] as a 1-element array
        board.write_analog(motor_chan, 1, np.array([0.5], dtype=np.float64))
        
        # 3. Read the encoder
        encoder_buffer = np.zeros(1, dtype=np.int32)
        board.read_encoder(encoder_chan, 1, encoder_buffer)
        
        print(f"Pos: {encoder_buffer[0]} counts", end="\r")
        time.sleep(0.01)

except HILError as e:
    print(f"\nHardware Error: {e.get_error_message()}")

finally:
    if board.is_valid():
        # Stop motor and disable amp
        board.write_analog(motor_chan, 1, np.zeros(1, dtype=np.float64))
        board.write_digital(enable_chan, 1, np.array([0], dtype=np.int32))
        board.close()
        print("\nHardware closed safely.")