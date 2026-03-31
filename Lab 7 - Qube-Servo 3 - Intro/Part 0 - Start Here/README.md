# QUBE-Servo 3 Lab: Python Control & Homing Example

This guide explains how to edit, understand, and run the Python scripts (`*.py` files) used to control the Quanser QUBE-Servo 3 hardware.

Note: Python files in this Github repository can be individually downloaded when working through Labs.

---

## 1. Script Overview: `homing.py`
The script uses a **Proportional (P) Controller** to move the motor to a specific angle. A topic you should be familiar with at this point.

When reading over the code, note that `#` denotes an inline comment. Anything proceeding the `#` symbol it there to explain what the code is doing in that section.

There is a lot of support code that allows the Python files to run the Qube-Servo 3 hardware, however you will only need to focus on the two sections of the code explained below.

### Control Parameters
This section of the code, located towards the top of the file, is where the variables you will adjust during your experiments live. Changes made here are equivilant to the input boxes you used in the last software.

```python
# Control Parameters
setpoint_deg = 0.0  # The target angle (where the arm tries to go)
Kp = 0.05           # Proportional Gain (Higher = more aggressive, Lower = smoother)
V_limit = 5.0       # Max voltage allowed (Safety limit)
```

### Control Logic
The heart of the script is the `while` loop. In the example code, the loop runs for 10 seconds, constantly calculating how much voltage to send to the motor based on the current "Error."

```python
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
```

---

## 2. How to Edit the Script
To change your control gains or setpoints, you need to open the code in a text editor.

1.  Open **File Explorer** and go to the folder containing your script.
2.  **Right-click** on `homing.py`.
3.  Hover over **Open with** and select **Notepad++**.
    * *If Notepad++ isn't listed, select "Choose another app" to find it, or use window's generic notepad*

---

## 3. How to Run the Script
Once you have saved your changes in Notepad++, follow these steps to execute the code:

1.  **Open a Terminal:** Right-click on an empty space inside the folder that contains the desired Python script, then select "Open PowerShell window here" or "Open in Terminal".
2.  **Run the Script:** Type the following command and press Enter:
```bash
python homing.py
```
3.  **View Results:** The script will run for 10 seconds. After it finishes, it will automatically generate a window with plots showing the Position and Error over time. If you need to cancel the current program you can press `ctl+c`.
