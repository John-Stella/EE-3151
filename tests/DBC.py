import time
import numpy as np
from quanser.hardware import HIL, HILError

# --- Hardware Config from Manual ---
board_type = "qube_servo3_usb"

# --- Constants from Manual ---
# 2048 counts/rev means 0.00307 rad per count 
K_RAD = 0.00307

# --- Channels ---
encoder_chans = np.array([0, 1], dtype=np.uint32)    # Position [cite: 79]
tach_chans = np.array([14000, 14001], dtype=np.uint32) # Velocity 
motor_chan = np.array([0], dtype=np.uint32)
enable_chan = np.array([0], dtype=np.uint32)

# --- Balancing Gains ---
K = np.array([-2.0, -1.5, 35.0, 3.0]) 

board = HIL()

try:
    board.open(board_type, "0")
    board.write_digital(enable_chan, 1, np.array([1], dtype=np.int32))
    
    print("Hold pendulum upright. Using Digital Tachometers for velocity...")
    input("Press Enter to start...")

    while True:
        # 1. Read Position (Encoders)
        counts = np.zeros(2, dtype=np.int32)
        board.read_encoder(encoder_chans, 2, counts)
        
        # 2. Read Velocity (Digital Tachometers) 
        # read_other is used for special channels > 10000
        tach_buffer = np.zeros(2, dtype=np.float64)
        board.read_other(tach_chans, 2, tach_buffer)
        
        # 3. Convert to Radians and Rad/s
        arm_pos = counts[0] * K_RAD
        raw_pend_angle = counts[1] * K_RAD
        
        # 3. Apply the 180-degree (pi) offset 
        # This makes Upright = 0 and Hanging = -pi
        pend_pos = raw_pend_angle - np.pi
        
        # 5. Optional: Wrap the angle to [-pi, pi] 
        # This keeps the math stable if the pendulum spins fully around
        pend_pos = (pend_pos + np.pi) % (2 * np.pi) - np.pi
        
        # Convert counts/sec to rad/sec [cite: 129, 164]
        arm_vel = tach_buffer[0] * K_RAD
        pend_vel = tach_buffer[1] * K_RAD
        
        # 6. Control Law
        state = np.array([arm_pos, arm_vel, pend_pos, pend_vel])
        voltage = np.dot(K, state)
        
        # Apply Deadband Compensation
        V_deadband = 0.65
        if abs(voltage) > 0.01: # Only apply if there is a command
            voltage += np.sign(voltage) * V_deadband
        
        # 7. Output & Safety
        voltage = np.clip(voltage, -4.0, 4.0)
        board.write_analog(motor_chan, 1, np.array([voltage], dtype=np.float64))
        
        # Safety break if it falls 
        if abs(pend_pos) > np.deg2rad(45):
            break

        time.sleep(0.002) # 500Hz - Tachometers allow for even faster loops!

except HILError as e:
    print(f"Hardware Error: {e.get_error_message()}")
finally:
    if board.is_valid():
        board.write_analog(motor_chan, 1, np.zeros(1, dtype=np.float64))
        board.write_digital(enable_chan, 1, np.array([0], dtype=np.int32))
        board.close()