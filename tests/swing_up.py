import time
import numpy as np
from quanser.hardware import HIL, HILError

# --- Hardware Constants from Manual ---
board_type = "qube_servo3_usb"
K_RAD = 0.00307  # 
Mp = 0.024       # Pendulum mass (kg) 
Lp = 0.129       # Pendulum length (m) 
g = 9.81         # Gravity (m/s^2)

# --- Control Parameters ---
# Swing-up gain (mu) and Balancing gains (K)
mu = 0.05
K = np.array([-2.0, -1.5, 35.0, 3.0]) 
catch_angle = np.deg2rad(20) # Switch to balance when within 20 degrees

board = HIL()

try:
    board.open(board_type, "0")
    # Enable motor amplifier [cite: 79, 131]
    board.write_digital(np.array([0], dtype=np.uint32), 1, np.array([1], dtype=np.int32))
    
    print("Swing-up active! Stand back—exposed moving parts.")
    
    prev_arm, prev_pend = 0.0, 0.0
    dt = 0.005
    start_time = time.time()

    while True:
        # 1. Read Encoders (Channel 0: Arm, Channel 1: Pendulum) [cite: 79]
        counts = np.zeros(2, dtype=np.int32)
        board.read_encoder(np.array([0, 1], dtype=np.uint32), 2, counts)
        
        # 2. Convert to Radians
        arm_pos = counts[0] * K_RAD
        # Shift pendulum angle so 0 is UP and PI/-PI is DOWN
        pend_pos = (counts[1] * K_RAD) % (2 * np.pi)
        if pend_pos > np.pi: pend_pos -= 2 * np.pi
            
        # 3. Calculate Velocities
        arm_vel = (arm_pos - prev_arm) / dt
        pend_vel = (pend_pos - prev_pend) / dt
        
        # 4. State Machine: Swing-up vs. Balance
        if abs(pend_pos) < catch_angle:
            # BALANCE MODE (State Feedback)
            state = np.array([arm_pos, arm_vel, pend_pos, pend_vel])
            voltage = -np.dot(K, state)
        else:
            # SWING-UP MODE (Energy Control)
            # Potential Energy reference is at the top
            pend_inertia = (1/3) * Mp * (Lp**2)
            energy = 0.5 * pend_inertia * (pend_vel**2) + Mp * g * (Lp/2) * (np.cos(pend_pos) - 1)
            # Acceleration command proportional to energy error
            accel = mu * energy * np.sign(pend_vel * np.cos(pend_pos))
            voltage = accel * 5.0 # Convert acceleration to voltage factor

        # 5. Safety Limits 
        voltage = np.clip(voltage, -10.0, 10.0)
        board.write_analog(np.array([0], dtype=np.uint32), 1, np.array([voltage], dtype=np.float64))
        
        prev_arm, prev_pend = arm_pos, pend_pos
        time.sleep(dt)

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    if board.is_valid():
        board.write_analog(np.array([0], dtype=np.uint32), 1, np.zeros(1, dtype=np.float64))
        board.write_digital(np.array([0], dtype=np.uint32), 1, np.array([0], dtype=np.int32))
        board.close()