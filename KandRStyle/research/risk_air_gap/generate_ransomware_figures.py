#!/usr/bin/env python3
"""
generate_ransomware_figures.py
===============================
Reproduce all ransomware Monte Carlo figures used in the KandR manuscript.

Usage:
    cd KandRStyle
    python3 research/risk_air_gap/generate_ransomware_figures.py

Outputs (written to KandRStyle/figures/):
    binary_ransomware_count.png
    histogram_ransomware.png
    histogram_ransomware_impact.png
    count_ransomware_percentile.png
    percent_ransomware_impact.png

See figures/README.txt for full methodology documentation.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# --- reproducibility ---
SEED = 42
np.random.seed(SEED)

# --- paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

# =============================================================
# DATA (from workbook: ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED.xlsx)
# =============================================================
YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022]

# American Samoa ransomware (all zeros)
AS_SCALED_COUNTS  = [0, 0, 0, 0, 0, 0, 0]
AS_CITY_LOSSES    = [0, 0, 0, 0, 0, 0, 0]

# California ransomware (scaled to Chattanooga population)
CA_SCALED_COUNTS  = [1, 1, 0, 1, 1, 2, 1.3927]
CA_CITY_LOSSES    = [774.79, 2705.98, 0.0, 4780.06, 3479.36, 29017.88, 6571.66]

as_mean_count   = sum(AS_SCALED_COUNTS) / len(YEARS)   # = 0.0
ca_mean_count   = sum(CA_SCALED_COUNTS) / len(YEARS)   # ≈ 1.056
as_mean_dollars = sum(AS_CITY_LOSSES)   / len(YEARS)   # = 0.0
ca_mean_dollars = sum(CA_CITY_LOSSES)   / len(YEARS)   # ≈ 6761.39

# Binary probability: midpoint of lower (AS) and upper (CA) means
PROB = (as_mean_count + ca_mean_count) / 2              # ≈ 0.528

N = 10_000
FIGSIZE = (12, 7.5)
DPI = 100


def save(name):
    path = os.path.join(FIGURES_DIR, name)
    plt.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'  saved → {path}')


# =============================================================
# 1. Binary count bar chart  (binary_ransomware_count.png)
# =============================================================
mc_counts = (np.random.random(N) < PROB).astype(int)
count_0 = int(np.sum(mc_counts == 0))
count_1 = int(np.sum(mc_counts == 1))
pct_0 = count_0 / N * 100
pct_1 = count_1 / N * 100

fig, ax = plt.subplots(figsize=FIGSIZE, facecolor='white')
ax.set_facecolor('white')
bars = ax.bar([0, 1], [pct_0, pct_1],
              color=['white', 'black'], edgecolor='black', linewidth=1.5, width=0.5)
for bar, val in zip(bars, [pct_0, pct_1]):
    ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.5,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=13, fontweight='bold')
ax.set_xlabel('Events', fontsize=14, fontweight='bold')
ax.set_ylabel('Likelihood (%)', fontsize=14, fontweight='bold')
ax.set_title('Monte Carlo Binary Simulation: Ransomware Event Count\n(10,000 Iterations)',
             fontsize=14, fontweight='bold')
ax.set_xticks([0, 1])
ax.set_xticklabels(['0', '1'], fontsize=13)
ax.set_ylim(0, 80)
ax.tick_params(axis='y', labelsize=12)
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', color='gray', linestyle='--', alpha=0.5)
plt.tight_layout()
save('binary_ransomware_count.png')

# =============================================================
# 2. Count histogram  (histogram_ransomware.png)
# =============================================================
fig, ax = plt.subplots(figsize=FIGSIZE, facecolor='white')
ax.set_facecolor('white')
ax.bar([0, 1], [count_0, count_1],
       color=['white', 'black'], edgecolor='black', linewidth=1.5, width=0.5)
for i, c in enumerate([count_0, count_1]):
    ax.text(i, c + 30, str(c), ha='center', va='bottom', fontsize=13, fontweight='bold')
ax.set_xlabel('Events', fontsize=14, fontweight='bold')
ax.set_ylabel('Count (out of 10,000)', fontsize=14, fontweight='bold')
ax.set_title('Monte Carlo Simulation: Ransomware Count\n(10,000 Iterations, Binary Distribution)',
             fontsize=14, fontweight='bold')
ax.set_xticks([0, 1])
ax.set_xticklabels(['0', '1'], fontsize=13)
ax.tick_params(axis='y', labelsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', color='gray', linestyle='--', alpha=0.5)
plt.tight_layout()
save('histogram_ransomware.png')

# =============================================================
# 3. Count percentile chart  (count_ransomware_percentile.png)
# =============================================================
sorted_counts = np.sort(mc_counts.astype(float))
pcts = np.arange(0, 101)
vals = np.percentile(sorted_counts, pcts)

fig, ax = plt.subplots(figsize=FIGSIZE, facecolor='white')
ax.set_facecolor('white')
ax.plot(vals, 100 - pcts, color='black', linewidth=2)
for level, ls in [(90, '--'), (50, ':'), (10, '-.')]:
    ax.axhline(y=level, color='gray', linestyle=ls, linewidth=1, label=f'{level}%')
ax.set_xlabel('Events', fontsize=14, fontweight='bold')
ax.set_ylabel('Probability of Exceeding', fontsize=14, fontweight='bold')
ax.set_title('Monte Carlo Simulation: Ransomware Event Percentiles\n(10,000 Iterations, Binary Distribution)',
             fontsize=14, fontweight='bold')
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))
ax.tick_params(labelsize=12)
ax.legend(fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(color='gray', linestyle='--', alpha=0.3)
plt.tight_layout()
save('count_ransomware_percentile.png')

# =============================================================
# 4. Impact histogram  (histogram_ransomware_impact.png)
# =============================================================
mc_impact = np.random.uniform(as_mean_dollars, ca_mean_dollars, N)

fig, ax = plt.subplots(figsize=FIGSIZE, facecolor='white')
ax.set_facecolor('white')
ax.hist(mc_impact, bins=50, color='gray', edgecolor='black', linewidth=0.5)
ax.set_xlabel('Impact ($)', fontsize=14, fontweight='bold')
ax.set_ylabel('Count', fontsize=14, fontweight='bold')
ax.set_title('Monte Carlo Simulation: Ransomware Impact\n(10,000 Iterations, Normal Distribution)',
             fontsize=14, fontweight='bold')
ax.tick_params(labelsize=12)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', color='gray', linestyle='--', alpha=0.5)
plt.tight_layout()
save('histogram_ransomware_impact.png')

# =============================================================
# 5. Impact percentile chart  (percent_ransomware_impact.png)
# =============================================================
sorted_impact = np.sort(mc_impact)
pct_vals = np.percentile(sorted_impact, pcts)

p10_val  = np.percentile(sorted_impact, 10)   # 90% chance ≥ this
p50_val  = np.percentile(sorted_impact, 50)   # 50% chance ≥ this
p90_val  = np.percentile(sorted_impact, 90)   # 10% chance ≥ this

fig, ax = plt.subplots(figsize=FIGSIZE, facecolor='white')
ax.set_facecolor('white')
ax.plot(pct_vals, 100 - pcts, color='black', linewidth=2)
for level, ls in [(90, '--'), (50, ':'), (10, '-.')]:
    ax.axhline(y=level, color='gray', linestyle=ls, linewidth=1, label=f'{level}%')
ax.set_xlabel('Cost ($)', fontsize=14, fontweight='bold')
ax.set_ylabel('Probability of Exceeding ($)', fontsize=14, fontweight='bold')
ax.set_title('Monte Carlo Simulation: Ransomware Impact Percentiles\n(10,000 Iterations)',
             fontsize=14, fontweight='bold')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d%%'))
ax.tick_params(labelsize=12)
ax.legend(fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(color='gray', linestyle='--', alpha=0.3)
plt.tight_layout()
save('percent_ransomware_impact.png')

# =============================================================
# Summary
# =============================================================
print()
print('=== Simulation Summary ===')
print(f'Seed:               {SEED}')
print(f'N iterations:       {N:,}')
print(f'AS mean count:      {as_mean_count:.4f}')
print(f'CA mean count:      {ca_mean_count:.4f}')
print(f'Binary probability: {PROB:.4f}')
print(f'P(0 events):        {pct_0:.1f}%')
print(f'P(1 event):         {pct_1:.1f}%')
print(f'CA mean dollars:    ${ca_mean_dollars:,.2f}')
print(f'Impact 10th pct:    ${p10_val:,.2f}   (90% chance ≥ this)')
print(f'Impact 50th pct:    ${p50_val:,.2f}  (50% chance ≥ this)')
print(f'Impact 90th pct:    ${p90_val:,.2f}  (10% chance ≥ this)')
print(f'80% CI:             [${p10_val:,.0f}, ${p90_val:,.0f}]')
