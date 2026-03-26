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

    print("Reading encoder for 5 seconds... Move the arm to see values change.")
    
    start_time = time.time()
    while time.time() - start_time < 10:
        # Pre-allocate the buffer
        encoder_counts = np.zeros(len(encoder_channels), dtype=np.int32)
        
        # Corrected call: added len(encoder_channels) as the second argument
        board.read_encoder(encoder_channels, len(encoder_channels), encoder_counts)
        
        print(f"Encoder Count (Channel 0): {encoder_counts[0]}", end="\n")
        time.sleep(0.5)

except HILError as e:
    print(f"\nA HIL error occurred: {e.get_error_message()}")

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    # 3. Always close the board to release hardware resources
    if board.is_valid():
        board.close()
        print("\nBoard connection closed.")