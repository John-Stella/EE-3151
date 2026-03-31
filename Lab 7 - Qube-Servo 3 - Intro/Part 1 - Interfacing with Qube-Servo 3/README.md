# Part 1 - Qube-Servo 3 Hardware Interfacing
This section of the lab focuses on the different hardware pieces and parameters available to us. These parts will determine how we are able to setup models and control logic for the Qube-Servo 3.

Each of the following sections relate to one of the provided Python scripts in this folder which showcase different parts of the control loop.

**!!! Please Attatch The Inertial Disk to the Qube-Servo 3 Before Continuing !!!**

---

## Encoder.py
Using the steps provided in part 0 of this lab, open and inspect the code.

Note that there is no 'control parameters' section to the code. This is because we will **not** be using the motor, only the encoder that reads the position of the motor shaft. The inital position(value of the encoder) is automatically set to 0 on power up. In addition, the next lab that focuses on the pendulum control will intoduce a second encoder that behaves similarly. 

```python
while true
        # 2. Read the encoder counts
        # The buffer must be a numpy array of the same size as encoder_channels
        encoder_counts = np.zeros(len(encoder_channels), dtype=np.int32)
        board.read_encoder(encoder_channels, encoder_counts)
        
        # Output the count for the first channel
        print(f"Encoder Count (Channel 0): {encoder_counts[0]}", end="\r")
        
        time.sleep(0.01) # 100Hz loop
```

Run the code and spin the Inertial Disk to set the behaivor of the encoder.

---

## Motor.py
This script shows us how to interface with the motor. It builds off the encoder script and includes code to write a voltage to the motor.

Note the 'control parameters' section in now available.

```python
# control parameters
voltage = 0.5;
```

```python
while time.time() - start_time < 3.0:
        # 2. Command 0.5V to the motor
        # Using [0.5] as a 1-element array
        board.write_analog(motor_chan, 1, np.array([0.5], dtype=np.float64))
        
        # 3. Read the encoder
        encoder_buffer = np.zeros(1, dtype=np.int32)
        board.read_encoder(encoder_chan, 1, encoder_buffer)
        
        print(f"Pos: {encoder_buffer[0]} counts", end="\r")
        time.sleep(0.01)
```

Run the code and test a couple differet voltages to see the response.

---

## pid.py
This script is a full implentation of a pid controller for an inertial load and includes a handy plotting function to visually inspect data.

Use what you have learned from previous labs to tune a decent PID controller (i.e. tune the kp, kd, ki).

```python
# control parameters
Kp, Ki, Kd = 0.001, 0.001, 0.001
amplitude, frequency = 90.0, 0.5 
```

```python
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
```
