"""
Experiment 9: Fuzzy Logic Controller (FLC) for Traffic Signal
AIM: Design and implement a Fuzzy Logic Controller that dynamically adjusts
     green light duration at an intersection based on traffic density and waiting time.
Requires: pip install scikit-fuzzy matplotlib numpy
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

print("Libraries imported successfully!")

# Define input and output variables
traffic_density = ctrl.Antecedent(np.arange(0, 51, 1), 'traffic_density')
waiting_time = ctrl.Antecedent(np.arange(0, 121, 1), 'waiting_time')
green_duration = ctrl.Consequent(np.arange(0, 91, 1), 'green_duration')

print("Input and Output variables defined.")

# Define membership functions for traffic density
traffic_density['low'] = fuzz.trapmf(traffic_density.universe, [0, 0, 5, 15])
traffic_density['medium'] = fuzz.trimf(traffic_density.universe, [10, 20, 30])
traffic_density['high'] = fuzz.trapmf(traffic_density.universe, [25, 35, 50, 50])

# Define membership functions for waiting time
waiting_time['short'] = fuzz.trapmf(waiting_time.universe, [0, 0, 10, 30])
waiting_time['moderate'] = fuzz.trimf(waiting_time.universe, [20, 50, 80])
waiting_time['long'] = fuzz.trapmf(waiting_time.universe, [70, 95, 120, 120])

# Define membership functions for green duration
green_duration['short'] = fuzz.trapmf(green_duration.universe, [0, 0, 10, 30])
green_duration['medium'] = fuzz.trimf(green_duration.universe, [20, 35, 55, 70])
green_duration['long'] = fuzz.trapmf(green_duration.universe, [60, 80, 90, 90])

# Visualize membership functions
traffic_density.view()
waiting_time.view()
green_duration.view()
plt.show()

# Define fuzzy rules
rule1 = ctrl.Rule(traffic_density['low'] & waiting_time['short'], green_duration['short'])
rule2 = ctrl.Rule(traffic_density['low'] & waiting_time['moderate'], green_duration['short'])
rule3 = ctrl.Rule(traffic_density['low'] & waiting_time['long'], green_duration['medium'])
rule4 = ctrl.Rule(traffic_density['medium'] & waiting_time['short'], green_duration['short'])
rule5 = ctrl.Rule(traffic_density['medium'] & waiting_time['moderate'], green_duration['medium'])
rule6 = ctrl.Rule(traffic_density['medium'] & waiting_time['long'], green_duration['long'])
rule7 = ctrl.Rule(traffic_density['high'] & waiting_time['short'], green_duration['medium'])
rule8 = ctrl.Rule(traffic_density['high'] & waiting_time['moderate'], green_duration['long'])
rule9 = ctrl.Rule(traffic_density['high'] & waiting_time['long'], green_duration['long'])

# Create control system
traffic_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
traffic_sim = ctrl.ControlSystemSimulation(traffic_ctrl)

# Generate 3D control surface
density_vals = np.linspace(0, 50, 30)
waiting_vals = np.linspace(0, 120, 30)
X, Y = np.meshgrid(density_vals, waiting_vals)
Z = np.zeros_like(X)

for i in range(len(waiting_vals)):
    for j in range(len(density_vals)):
        try:
            traffic_sim.input['traffic_density'] = X[i, j]
            traffic_sim.input['waiting_time'] = Y[i, j]
            traffic_sim.compute()
            Z[i, j] = traffic_sim.output['green_duration']
        except ValueError:
            Z[i, j] = 0

# Plot 3D surface
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(projection='3d')
surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.9)

ax.set_title('Traffic Signal Fuzzy Control Surface')
ax.set_xlabel('Traffic Density (veh/min)')
ax.set_ylabel('Waiting Time (sec)')
ax.set_zlabel('Green Duration (sec)')
fig.colorbar(surf, shrink=0.5, aspect=5, label='Green Duration (sec)')

plt.show()
