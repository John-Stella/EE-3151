import time
import numpy as np
import matplotlib.pyplot as plt  # Added for plotting
from quanser.hardware import HIL, HILError

# Config
board_type = "qube_servo3_usb"
board_identifier = "0"

# Calibration constants
COUNTS_PER_REV = 2048
DEG_PER_COUNT = 360.0 / COUNTS_PER_REV

# Channels
encoder_chan = np.array([0], dtype=np.uint32)
motor_chan = np.array([0], dtype=np.uint32)
enable_chan = np.array([0], dtype=np.uint32)

# Define object
board = HIL()

# Control Parameters
setpoint_deg = 0.0  
Kp = 0.05           
V_limit = 5.0       

# Data logging lists
time_log = []
pos_log = []
error_log = []

try:
    board.open(board_type, board_identifier)
    board.write_digital(enable_chan, 1, np.array([1], dtype=np.int32))
    
    print(f"Homing to {setpoint_deg}°. Logging data for 10 seconds...")
    
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > 10.0:
            break
            
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
        
        # 6. Log Data
        time_log.append(elapsed_time)
        pos_log.append(current_pos_deg)
        error_log.append(error)
        
        time.sleep(0.01)

except HILError as e:
    print(f"\nHardware Error: {e.get_error_message()}")
finally:
    # Safely stop hardware
    if board.is_valid():
        board.write_analog(motor_chan, 1, np.zeros(1, dtype=np.float64))
        board.write_digital(enable_chan, 1, np.array([0], dtype=np.int32))
        board.close()
        print("\nHardware closed. Generating plots...")

    # --- Plotting Section ---
    plt.figure(figsize=(10, 6))
    
    # Subplot 1: Position
    plt.subplot(2, 1, 1)
    plt.plot(time_log, pos_log, label='Current Position', color='blue')
    plt.axhline(y=setpoint_deg, color='red', linestyle='--', label='Setpoint')
    plt.title('Homing Performance')
    plt.ylabel('Position (deg)')
    plt.legend()
    plt.grid(True)

    # Subplot 2: Error
    plt.subplot(2, 1, 2)
    plt.plot(time_log, error_log, label='Error', color='green')
    plt.xlabel('Time (s)')
    plt.ylabel('Error (deg)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()