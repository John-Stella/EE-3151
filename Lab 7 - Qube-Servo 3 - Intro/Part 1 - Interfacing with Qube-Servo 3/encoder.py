import time
import numpy as np
from quanser.hardware import HIL, HILError

# Hardware configuration
board_type = "qube_servo3_usb"
board_identifier = "0"
encoder_channels = np.array([0], dtype=np.uint32)  # Channel 0 is the motor arm

# Initialize the HIL board
board = HIL()

try:
    # 1. Open the connection to the Qube-Servo 3
    print(f"Opening {board_type}...")
    board.open(board_type, board_identifier)

    print("Reading encoder. Move the arm to see values change. Press Ctrl+C to exit")
    
    while True:
        # 2. Read the encoder counts
        # The buffer must be a numpy array of the same size as encoder_channels
        encoder_counts = np.zeros(1, dtype=np.int32)
        board.read_encoder(encoder_channels, 1, encoder_counts)
        
        # Output the count for the first channel
        print(f"Encoder Count (Channel 0): {encoder_counts[0]}", end="\r")
        
        time.sleep(0.01) # 100Hz loop

except HILError as e:
    print(f"\nA HIL error occurred: {e.get_error_message()}")

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    # 3. Always close the board to release hardware resources
    if board.is_valid():
        board.close()
        print("\nBoard connection closed.")