import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))

from src.constants import *
from src.utils.imports import *
from src.utils.utils import *

# Data definition
data = {
    "Variable": ["RGDP", "NGDP", "UNEMP", "RNRESIN", "RRESIN"],
    "Individual Before 2000": [-0.224, -0.294, 0.141, -0.193, -0.258],
    "Individual After 2000": [-0.439, -0.309, -0.281, -0.302, -0.236],
    "Consensus Before 2000": [0.543, 0.406, 0.650, 0.743, 0.783],
    "Consensus After 2000": [-0.385, -0.108, -0.224, -0.012, 0.312],
    "Idiosyncratic Before 2000": [-0.442, -0.430, -0.190, -0.419, -0.504],
    "Idiosyncratic After 2000": [-0.504, -0.511, -0.356, -0.559, -0.472],
    "Weight Before 2000": [77.87, 83.73, 60.60, 80.55, 80.89],
    "Weight After 2000": [45.38, 49.88, 43.18, 53.02, 69.90]
}

df = pd.DataFrame(data)

# Plot configuration
plt.rcParams.update({'font.size': 16})  # Updating font size and weight
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 12))
bar_width = 0.35
index = np.arange(len(df))
colors = ["#000000", "#808080"]  # Using vivid green and red for clear distinction

# Individual Coefficients
axes[0, 0].bar(index - bar_width/2, df["Individual Before 2000"], bar_width, label='Before 2000', color=colors[0])
axes[0, 0].bar(index + bar_width/2, df["Individual After 2000"], bar_width, label='After 2000', color=colors[1])
axes[0, 0].set_title('Individual Coefficients')
axes[0, 0].set_xticks(index)
axes[0, 0].set_xticklabels(df["Variable"], rotation=45)

# Consensus Coefficients
axes[0, 1].bar(index - bar_width/2, df["Consensus Before 2000"], bar_width, label='Before 2000', color=colors[0])
axes[0, 1].bar(index + bar_width/2, df["Consensus After 2000"], bar_width, label='After 2000', color=colors[1])
axes[0, 1].set_title('Consensus Coefficients')
axes[0, 1].set_xticks(index)
axes[0, 1].set_xticklabels(df["Variable"], rotation=45)

# Idiosyncratic Coefficients
axes[1, 0].bar(index - bar_width/2, df["Idiosyncratic Before 2000"], bar_width, label='Before 2000', color=colors[0])
axes[1, 0].bar(index + bar_width/2, df["Idiosyncratic After 2000"], bar_width, label='After 2000', color=colors[1])
axes[1, 0].set_title('Idiosyncratic Coefficients')
axes[1, 0].set_xticks(index)
axes[1, 0].set_xticklabels(df["Variable"], rotation=45)

# Weights
axes[1, 1].bar(index - bar_width/2, df["Weight Before 2000"], bar_width, label='Before 2000', color=colors[0])
axes[1, 1].bar(index + bar_width/2, df["Weight After 2000"], bar_width, label='After 2000', color=colors[1])
axes[1, 1].set_title('Weights on Idiosyncratic')
axes[1, 1].set_xticks(index)
axes[1, 1].set_xticklabels(df["Variable"], rotation=45)
i=0
# Global settings
for ax in axes.flat:
    i+=1
    # ax.set_xlabel("Variable")
    if i<4:
        ax.set_ylabel("Coefficients")
    elif i ==4:
        ax.set_ylabel("Weights(%)")
    ax.grid(True, linestyle='--', alpha=0.6)  # Add gridlines for better readability

# Add a legend to explain colors
fig.legend(
    ["Before 2000", "After 2000"],
    loc="lower center",
    ncol=2,
    frameon=False,
    fontsize="large",
)

plt.tight_layout()

fig.subplots_adjust(bottom=0.14, top=0.95)

plt.show()
