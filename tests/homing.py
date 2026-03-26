import time
import numpy as np
from quanser.hardware import HIL, HILError

# Config
board_type = "qube_servo3_usb"
board_identifier = "0"

# Calibration constants
COUNTS_PER_REV = 2048
DEG_PER_COUNT = 360.0 / COUNTS_PER_REV

# Control Parameters
setpoint_deg = 0.0  # Target position
Kp = 0.05           # Proportional Gain (Adjust this if it's too weak or oscillates)
V_limit = 5.0       # Max voltage for safety

# Channels
encoder_chan = np.array([0], dtype=np.uint32)
motor_chan = np.array([0], dtype=np.uint32)
enable_chan = np.array([0], dtype=np.uint32)

board = HIL()

try:
    board.open(board_type, board_identifier)
    board.write_digital(enable_chan, 1, np.array([1], dtype=np.int32))
    
    print(f"Homing to {setpoint_deg} degrees. Try moving the arm by hand!")
    
    start_time = time.time()
    while time.time() - start_time < 10.0: # Run for 10 seconds
        # 1. Read position
        encoder_buffer = np.zeros(1, dtype=np.int32)
        board.read_encoder(encoder_chan, 1, encoder_buffer)
        
        # 2. Convert to degrees
        current_pos_deg = encoder_buffer[0] * DEG_PER_COUNT
        
        # 3. Calculate Control Signal (P-Controller)
        error = setpoint_deg - current_pos_deg
        voltage = Kp * error
        
        # 4. Saturation (Safety Limit)
        voltage = np.clip(voltage, -V_limit, V_limit)
        
        # 5. Write to motor
        board.write_analog(motor_chan, 1, np.array([voltage], dtype=np.float64))
        
        print(f"Pos: {current_pos_deg:6.2f}° | Error: {error:6.2f}° | Out: {voltage:5.2f}V", end="\r")
        time.sleep(0.01)

except HILError as e:
    print(f"\nHardware Error: {e.get_error_message()}")
finally:
    if board.is_valid():
        board.write_analog(motor_chan, 1, np.zeros(1, dtype=np.float64))
        board.write_digital(enable_chan, 1, np.array([0], dtype=np.int32))
        board.close()
        print("\nControl stopped and board closed.")