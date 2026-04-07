# Lab 8 Section 2
In this section we will construct the control system that will balance the pendulum.

---

## Part 1 - Building the Control Logic
![figure]()

In the last section I introduced the PD equation and its parts. Let's learn how to build it.

Open the `balance.py` script in Notepad++. You will be adding code provided in this section to contruct the PD controller. *Note: You must save your work before running the script. You do not need to close the Notepad++ doc between test runs.*

### Add the PD Control Gains
Find the section of code that looks like the block below:
 
```python
    # ------------------------------------------------------------------------------------------
    # Control Gains
    # Define a vector that contains the following PD control gain constants
    # 
    K = #[Replace this with a vector of the four control gains, don't forget to remove the '#']
    # ------------------------------------------------------------------------------------------
```

Construct a vector using the example method and table shown below. We use Numpy arrays (`np.array()`) because it hold variables in a convenient format for mathematical operations, like MATLAB matricies. 

```python
np.array([k_p_theta, k_p_alpha, k_d_theta, k_d_alpha])
```

| Gain Constant | Symbol | Value |
| :--- | :--- | :--- |
| **Motor Proportional Gain** | $k_{p,\theta}$ | -2.0 |
| **Pendulum Proportional Gain** | $k_{p,\alpha}$ | 30.0 |
| **Motor Derivative Gain** | $k_{d,\theta}$ | -2.0 |
| **Pendulum Derivative Gain** | $k_{d,\alpha}$ | 2.5 |

### Motor Target Position
Lets now define the angle for the motor to balance around. Note this is not the pendulum angle, but the angle show on the base of the Qube-Servo 3.

In the section:
```python
# User Build Area ----------------------------------------------------------------------------
# Add code inside the lines

# --------------------------------------------------------------------------------------------
``` 

Add a variable that targets an angle between $\pm 45^\circ$:
```python
a_descriptive_variable_name = an_angle_to_target
``` 

### Define the State Varibles
In this part we will collect the state variables that were used in section 1. We once again want to Numpy arrays so we can do math on the numbers inside the vectors. Think of this vector as the collection of terms from our equation $u = k_{p,\theta}(\theta_r - \theta) - k_{p,\alpha}\alpha - k_{d,\theta}\dot{\theta} - k_{d,\alpha}\dot{\alpha}$ with the K-terms factored out into its own term.

**Below the last line of code you added** add another line that mimics the structure of your K Control Gain vector previously defined. It is important that these two vectors are the same size so we can use matix math on them. **Use these names for the vector elements in the provided order:**

```python
theta, alpha, theta_dot, alpha_dot
``` 

```python
states = np.array([])
``` 

#### State Varible Adjustments
We need to adjust the elements of the `states` vector to include relative term infomation from the equation:

$$u = k_{p,\theta}(\theta_r - \theta) - k_{p,\alpha}\alpha - k_{d,\theta}\dot{\theta} - k_{d,\alpha}\dot{\alpha}$$

For the `theta` element we need to subtract it from the target angle and convert the target angle from degrees to radians. Do this by editing the `states =` line.

> Multiply your target variable name by pi(use `np.pi` which compiles as 3.14...), divide it by 180, then subtract `theta`. Use this equation as the first term in your vector.

> The rest of the terms are simply negated in the equation, do this by adding `-` infront of each variable name.

### Calculte the Output Voltage
We want to implement a safety system into the control logic that disables the motor if the pendulum is too far outside the balance point. This prevents the motor and pendulum from swinging out of control. It is written in python like this:

```python
			if alpha_degrees > 10:
                voltage = 0
            else:
                voltage = 
``` 

We can now calculate the output voltage of the balance control signal. The original voltage control signal can be recontructed by from our vectors by performing the dot product of the two vectors.

```python
np.dot(vec1, vec2)
``` 

We also need to reverse the direction of the signal to account for inverse motor wiring. *A Qube-Servo 3 querk.* Multiply the dot product by `-1` in the same line.

**At this point your control logic should be complete. The rest of the python script will use the code to provide the Qube-Servo 3 a control signal and plot the state variables.**

## Part 2 - Run the Script 
Save and Run the Python Code, then answer the following problems. 