import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Simulation parameters
# -----------------------------
T = 30                             # timesteps
threshold = 0.24                   # detection threshold (lowered)
patience = 1                       # timesteps required to trigger
collusion_start = 6                # attack onset
mitigation_strength = 0.35         # how strongly intervention reduces collusion

# -----------------------------
# State variables
# -----------------------------
concentration = np.zeros(T)
within_cluster_share = np.zeros(T)
intervention = np.zeros(T)

# -----------------------------
# Generate dynamics
# -----------------------------
above_threshold_counter = 0
intervention_active = False

for t in range(T):

    if t < collusion_start:
        # benign regime
        within_cluster_share[t] = 0.01 + 0.005 * np.random.rand()
    else:
        # collusion regime
        if not intervention_active:
            within_cluster_share[t] = 0.25 + 0.03 * np.random.randn()
        else:
            # mitigation effect
            within_cluster_share[t] = (
                within_cluster_share[t - 1] * (1 - mitigation_strength)
                + 0.05 * np.random.rand()
            )

    # clip to valid range
    within_cluster_share[t] = np.clip(within_cluster_share[t], 0.0, 0.35)

    # concentration metric (smoothed)
    if t == 0:
        concentration[t] = within_cluster_share[t]
    else:
        concentration[t] = 0.7 * concentration[t - 1] + 0.3 * within_cluster_share[t]

    # detection logic
    if concentration[t] > threshold:
        above_threshold_counter += 1
    else:
        above_threshold_counter = 0

    if above_threshold_counter >= patience:
        intervention_active = True

    intervention[t] = 1 if intervention_active else 0

# -----------------------------
# Plot
# -----------------------------
fig, axes = plt.subplots(3, 1, figsize=(8, 7), sharex=True)

# Panel 1: concentration
axes[0].plot(concentration, linewidth=2, label="Concentration metric")
axes[0].axhline(threshold, linestyle="--", color="orange", label="Detection threshold")
axes[0].set_ylabel("Concentration")
axes[0].legend()
axes[0].set_title("Collusion / cluster capture detection and mitigation")

# Panel 2: within-cluster share
axes[1].plot(within_cluster_share, linewidth=2, label="Within-cluster co-review share")
axes[1].set_ylabel("Within-cluster share")
axes[1].legend()

# Panel 3: intervention
axes[2].step(range(T), intervention, where="post", linewidth=2,
             label="Intervention (decentralize / rotate)")
axes[2].set_ylabel("Intervention")
axes[2].set_yticks([0, 1])
axes[2].set_yticklabels(["OFF", "ON"])
axes[2].set_xlabel("Timestep")
axes[2].legend()

plt.tight_layout()
plt.savefig("fig8_collusion_capture.png", dpi=300)
plt.show()
