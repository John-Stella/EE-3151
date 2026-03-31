import time
import numpy as np
import matplotlib.pyplot as plt
from quanser.hardware import HIL, HILError

# --- Hardware Config ---
board_type = "qube_servo3_usb"
board_identifier = "0"
COUNTS_PER_REV = 2048
DEG_PER_COUNT = 360.0 / COUNTS_PER_REV

# --- PID Gains ---
Kp, Ki, Kd = 0.12, 0.01, 0.005
amplitude, frequency = 90.0, 0.5 

# --- Data Collection ---
times, setpoints, positions = [], [], []

board = HIL()
try:
    board.open(board_type, board_identifier)
    board.write_digital(np.array([0], dtype=np.uint32), 1, np.array([1], dtype=np.int32))
    
    print("Tracking +/- 90 degrees. Press Ctrl+C to stop.")
    
    integral_error, last_error, dt = 0.0, 0.0, 0.01
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        setpoint = amplitude * np.sin(2 * np.pi * frequency * elapsed)
        
        encoder_buffer = np.zeros(1, dtype=np.int32)
        board.read_encoder(np.array([0], dtype=np.uint32), 1, encoder_buffer)
        current_pos = encoder_buffer[0] * DEG_PER_COUNT
        
        error = setpoint - current_pos
        integral_error += error * dt
        derivative_error = (error - last_error) / dt
        
        voltage = np.clip((Kp * error) + (Ki * integral_error) + (Kd * derivative_error), -10, 10)
        board.write_analog(np.array([0], dtype=np.uint32), 1, np.array([voltage], dtype=np.float64))
        
        # Log data
        times.append(elapsed)
        setpoints.append(setpoint)
        positions.append(current_pos)
        
        last_error = error
        time.sleep(dt)

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    if board.is_valid():
        board.write_analog(np.array([0], dtype=np.uint32), 1, np.zeros(1, dtype=np.float64))
        board.write_digital(np.array([0], dtype=np.uint32), 1, np.zeros(1, dtype=np.int32))
        board.close()
        
    # --- Plotting ---
    plt.figure(figsize=(10, 5))
    plt.plot(times, setpoints, 'r--', label="Target Path")
    plt.plot(times, positions, 'b-', label="Arm Position")
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (Degrees)")
    plt.title("PID Tracking Performance: Qube-Servo 3")
    plt.legend()
    plt.grid(True)
    plt.show()