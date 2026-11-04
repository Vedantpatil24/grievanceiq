"""
Experiment 10: ANFIS - Adaptive Neural Fuzzy Inference System
AIM: Design and implement an ANFIS model to predict daily household energy
     consumption based on temperature, humidity, appliance usage, and occupancy.
Requires: pip install torch numpy pandas scikit-learn matplotlib
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Set random seed for reproducibility
torch.manual_seed(42)
np.random.seed(42)


# ==========================================
# 1. DATA GENERATION & PREPROCESSING
# ==========================================
def generate_household_data(num_samples=1000):
    """Generates realistic synthetic daily household energy consumption data."""
    np.random.seed(42)
    temperature = np.random.uniform(10.0, 40.0, num_samples)
    humidity = np.random.uniform(20.0, 90.0, num_samples)
    appliances = np.random.uniform(1.0, 10.0, num_samples)
    occupancy = np.random.randint(0, 5, num_samples).astype(float)

    # Non-linear energy consumption formula with noise
    energy = (
        2.5 * (temperature - 20)**2 / 100 +
        1.2 * appliances +
        0.8 * occupancy +
        0.05 * humidity +
        np.random.normal(0, 1.0, num_samples)
    )
    energy = np.clip(energy + 10, 5.0, 50.0)

    df = pd.DataFrame({
        'Temperature': temperature,
        'Humidity': humidity,
        'Appliances': appliances,
        'Occupancy': occupancy,
        'Energy': energy
    })
    return df


# Load dataset
df = generate_household_data(1200)
X = df[['Temperature', 'Humidity', 'Appliances', 'Occupancy']].values
y = df['Energy'].values

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalization
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

# Convert to Tensors
X_train_t = torch.tensor(X_train_scaled, dtype=torch.float32)
y_train_t = torch.tensor(y_train_scaled, dtype=torch.float32).unsqueeze(1)
X_test_t = torch.tensor(X_test_scaled, dtype=torch.float32)
y_test_t = torch.tensor(y_test_scaled, dtype=torch.float32).unsqueeze(1)


# ==========================================
# 2. ANFIS MODEL ARCHITECTURE (SUGENO TYPE)
# ==========================================
class SimpleANFIS(nn.Module):
    def __init__(self, num_inputs=4, num_mfs=2):
        super(SimpleANFIS, self).__init__()
        self.num_inputs = num_inputs
        self.num_mfs = num_mfs
        self.num_rules = num_mfs ** num_inputs  # e.g., 2^4 = 16 rules

        # Premise parameters (Gaussian MFs: centers 'mu' and sigmas 'sigma')
        self.mu = nn.Parameter(torch.rand(num_inputs, num_mfs))
        self.sigma = nn.Parameter(torch.ones(num_inputs, num_mfs) * 0.5)

        # Consequent parameters (Linear coefficients for each rule)
        self.consequent_weights = nn.Parameter(
            torch.randn(self.num_rules, num_inputs + 1) * 0.1
        )

    def forward(self, x):
        batch_size = x.size(0)

        # Layer 1: Fuzzification (Gaussian MFs)
        x_expanded = x.unsqueeze(2)
        mu = self.mu.unsqueeze(0)
        sigma = torch.abs(self.sigma).unsqueeze(0) + 1e-6

        membership = torch.exp(-((x_expanded - mu) ** 2) / (2 * (sigma ** 2)))

        # Layer 2: Rule Layer (Firing strengths via T-norm / Product)
        rule_firing = []
        indices = list(np.ndindex(*(self.num_mfs,) * self.num_inputs))

        for idxs in indices:
            firing = torch.ones(batch_size, device=x.device)
            for i, mf_idx in enumerate(idxs):
                firing = firing * membership[:, i, mf_idx]
            rule_firing.append(firing)

        w = torch.stack(rule_firing, dim=1)

        # Layer 3: Normalization Layer
        w_sum = torch.sum(w, dim=1, keepdim=True) + 1e-8
        w_normalized = w / w_sum

        # Layer 4: Consequent Layer (TSK linear outputs)
        ones = torch.ones(batch_size, 1, device=x.device)
        x_bias = torch.cat([x, ones], dim=1)
        rule_outputs = torch.matmul(x_bias, self.consequent_weights.T)

        # Layer 5: Output Layer (Aggregated crisp sum)
        output = torch.sum(w_normalized * rule_outputs, dim=1, keepdim=True)
        return output


# Initialize model, loss function, and optimizer
model = SimpleANFIS(num_inputs=4, num_mfs=2)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)


# ==========================================
# 3. MODEL TRAINING (GRADIENT DESCENT)
# ==========================================
epochs = 200
print("Starting ANFIS Model Training...")
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()

    outputs = model(X_train_t)
    loss = criterion(outputs, y_train_t)

    loss.backward()
    optimizer.step()

    if (epoch + 1) % 40 == 0:
        print(f"Epoch [{epoch+1}/{epochs}], Loss (MSE): {loss.item():.4f}")


# ==========================================
# 4. EVALUATION & TESTING
# ==========================================
model.eval()
with torch.no_grad():
    y_pred_scaled = model(X_test_t).numpy()

# Inverse transform predictions back to original scale (kWh)
y_pred = scaler_y.inverse_transform(y_pred_scaled).flatten()

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n--- Model Performance Evaluation ---")
print(f"Root Mean Squared Error (RMSE): {rmse:.4f} kWh")
print(f"Mean Absolute Error (MAE): {mae:.4f} kWh")
print(f"R-squared Score (R2): {r2:.4f}")


# ==========================================
# 5. VISUALIZATION
# ==========================================
plt.figure(figsize=(12, 5))

# Plot 1: Predicted vs Actual
plt.subplot(1, 2, 1)
plt.scatter(y_test, y_pred, alpha=0.7, color='teal', edgecolors='k')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, label='Ideal Fit')
plt.xlabel('Actual Energy Consumption (kWh)')
plt.ylabel('Predicted Energy Consumption (kWh)')
plt.title('ANFIS: Actual vs Predicted Energy')
plt.legend()
plt.grid(True)

# Plot 2: Time Series Comparison (First 50 samples)
plt.subplot(1, 2, 2)
plt.plot(y_test[:50], label='Actual', marker='o', color='royalblue')
plt.plot(y_pred[:50], label='Predicted (ANFIS)', marker='x', color='darkorange', linestyle='--')
plt.xlabel('Sample Index')
plt.ylabel('Energy Consumption (kWh)')
plt.title('Energy Consumption Trend Comparison')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
