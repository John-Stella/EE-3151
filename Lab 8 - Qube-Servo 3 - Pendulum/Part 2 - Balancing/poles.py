#import control as ct
import numpy as np

# System Defined A and B Matrices
#
# These come from solving the open-loop system x_dot = Ax + Bu for u = -Kx
#
#  x_dot = (A - KB)x
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