import time
import numpy as np
from quanser.hardware import HIL, HILError

# --- Hardware Config from Manual ---
board_type = "qube_servo3_usb"
board_identifier = "0"
K_RAD = 0.00307  # Radians per count 

# --- Balancing Gains (Typical for Qube-Servo 3) ---
# Format: [Arm_Pos, Arm_Vel, Pend_Pos, Pend_Vel]
K = np.array([-2.0, -1.5, 35.0, 3.0]) 

# --- Channels ---
encoder_chans = np.array([0, 1], dtype=np.uint32) # 0=Arm, 1=Pendulum 
motor_chan = np.array([0], dtype=np.uint32)
enable_chan = np.array([0], dtype=np.uint32)

board = HIL()

try:
    board.open(board_type, board_identifier)
    board.write_digital(enable_chan, 1, np.array([1], dtype=np.int32))
    
    print("HOLD PENDULUM UPRIGHT and press Enter to begin balancing...")
    input()

    # State variables
    prev_arm_pos, prev_pend_pos = 0.0, 0.0
    dt = 0.005 # 200Hz loop for better stability
    
    start_time = time.time()
    while True:
        # 1. Read Encoders
        counts = np.zeros(2, dtype=np.int32)
        board.read_encoder(encoder_chans, 2, counts)
        
        # 2. Convert to Radians
        # Pendulum starts at 0 rad when held upright
        arm_pos = counts[0] * K_RAD
        pend_pos = counts[1] * K_RAD
        
        # 3. Calculate Velocities (Numerical Differentiation)
        arm_vel = (arm_pos - prev_arm_pos) / dt
        pend_vel = (pend_pos - prev_pend_pos) / dt
        
        # 4. State Feedback Control Law: V = -(K1*theta + K2*theta_dot + K3*alpha + K4*alpha_dot)
        # Note: alpha is the pendulum angle. If it falls, error increases.
        state = np.array([arm_pos, arm_vel, pend_pos, pend_vel])
        voltage = -np.dot(K, state)
        
        # 5. Safety Limits
        # Manual recommends +/- 10V 
        voltage = np.clip(voltage, -4.0, 4.0)
        
        # If the pendulum falls too far (> 30 degrees), stop for safety
        if abs(pend_pos) > np.deg2rad(30):
            print("\nPendulum fell! Shutting down...")
            break
            
        board.write_analog(motor_chan, 1, np.array([voltage], dtype=np.float64))
        
        # Update state
        prev_arm_pos, prev_pend_pos = arm_pos, pend_pos
        time.sleep(dt)

except KeyboardInterrupt:
    print("\nStopped by user.")
except HILError as e:
    print(f"\nHardware Error: {e.get_error_message()}")
finally:
    if board.is_valid():
        board.write_analog(motor_chan, 1, np.zeros(1, dtype=np.float64))
        board.write_digital(enable_chan, 1, np.array([0], dtype=np.int32))
        board.close()
        print("Board closed safely.")