import time
import numpy as np
from quanser.hardware import HIL, HILError

# --- Config ---
board_type = "qube_servo3_usb"
board_identifier = "0"
COUNTS_PER_REV = 2048
DEG_PER_COUNT = 360.0 / COUNTS_PER_REV

# --- PID Gains (Tuned for Qube-Servo 3) ---
Kp = 0.12     # Proportional
Ki = 0.01     # Integral (Keep low to start)
Kd = 0.005    # Derivative (Smooths motion)

# --- Path Parameters ---
amplitude = 90.0  # Degrees (+/- 90)
frequency = 0.5   # Hz (One full cycle every 2 seconds)
V_limit = 10.0    # Voltage limit

# --- Channels ---
encoder_chan = np.array([0], dtype=np.uint32)
motor_chan = np.array([0], dtype=np.uint32)
enable_chan = np.array([0], dtype=np.uint32)

board = HIL()

try:
    board.open(board_type, board_identifier)
    board.write_digital(enable_chan, 1, np.array([1], dtype=np.int32))
    
    print("PID Tracking started. Arm will swing +/- 90 degrees.")
    
    # PID state variables
    integral_error = 0.0
    last_error = 0.0
    dt = 0.01  # 10ms loop time
    
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        
        # 1. Generate Setpoint (Sine Wave)
        # target = Amp * sin(2 * pi * f * t)
        setpoint = amplitude * np.sin(2 * np.pi * frequency * elapsed)
        
        # 2. Read Sensors
        encoder_buffer = np.zeros(1, dtype=np.int32)
        board.read_encoder(encoder_chan, 1, encoder_buffer)
        current_pos = encoder_buffer[0] * DEG_PER_COUNT
        
        # 3. PID Calculation
        error = setpoint - current_pos
        integral_error += error * dt
        derivative_error = (error - last_error) / dt
        
        voltage = (Kp * error) + (Ki * integral_error) + (Kd * derivative_error)
        
        # 4. Safety & Write
        voltage = np.clip(voltage, -V_limit, V_limit)
        board.write_analog(motor_chan, 1, np.array([voltage], dtype=np.float64))
        
        # Update state
        last_error = error
        
        print(f"Target: {setpoint:6.1f}° | Actual: {current_pos:6.1f}° | Out: {voltage:5.2f}V", end="\r")
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
        print("\nSafe shutdown complete.")