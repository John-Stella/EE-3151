#import control as ct
import numpy as np
import matplotlib.pyplot as plt

# System Defined A and B Matrices
#
# These come from solving the acceleration terms of the rotary pendulum once linearized using system parameters.
#
# Do Not Change These Values
A = np.array([[0,0,1,0],[0,0,0,1],[0,55.1525,-4.5471,-0.1816],[0,168.5810,-4.4942,-0.5551]], dtype=np.float64) 
B = np.array([0,0,20.6755,20.4351], dtype=np.float64)

# Your hand-tuned gains
# Put your values here in this order
# [k_p_theta, k_p_alpha, k_d_theta, k_d_alpha]
K = np.array([ , , , ], dtype=np.float64)

# Calculate closed-loop poles
closed_loop_matrix = A - B @ K
poles = np.linalg.eigvals(closed_loop_matrix)
print(poles)

# --- PLOTTING CODE ---

# 1. Extract real and imaginary parts
real_parts = poles.real
imag_parts = poles.imag

# 2. Create the plot
plt.figure(figsize=(8, 6))

# Use 'x' marker as is standard for poles
plt.scatter(real_parts, imag_parts, marker='x', color='red', s=100, label='Closed-loop Poles')

# 3. Add axes and labels
plt.axhline(0, color='black', lw=1) # Real axis line
plt.axvline(0, color='black', lw=1) # Imaginary axis line

plt.title('Pole-Zero Map (S-Plane)')
plt.xlabel('Real Axis ($\sigma$)')
plt.ylabel('Imaginary Axis ($j\omega$)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# 4. Set plot limits to see the origin clearly
limit = max(max(abs(real_parts)), max(abs(imag_parts)), 1) + 1
plt.xlim(-limit, limit)
plt.ylim(-limit, limit)

plt.show()