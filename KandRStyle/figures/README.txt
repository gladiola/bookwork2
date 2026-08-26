README.txt — Figures Directory
Ransomware Section Graph Reproduction Guide
===========================================

This file documents how the ransomware Monte Carlo figures were produced using
NumPy and Matplotlib, so that results can be reproduced exactly.

ENVIRONMENT
-----------
  Python  >= 3.10
  numpy   >= 1.24
  matplotlib >= 3.7
  Pillow  >= 10.0 (optional, for image inspection)

Install dependencies:
  pip install numpy matplotlib pillow

RANDOM SEED
-----------
  numpy.random.seed(42) and random.seed(42) are set before all simulations.
  Rerunning the script with these seeds will reproduce the exact figures.

DATA SOURCES
------------
  All raw counts and dollar losses were extracted from the workbook:
    ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED.xlsx

  American Samoa Ransomware (2016–2022):
    Raw counts:          0, 0, 0, 0, 0, 0, 0
    Per-capita rates:    0, 0, 0, 0, 0, 0, 0
    Scaled counts:       0, 0, 0, 0, 0, 0, 0
    Projected city loss: $0 for all years
    Mean scaled count:   0.00
    Mean scaled dollars: $0.00

  California Ransomware (2016–2022):
    Raw counts:          336, 222, 211, 303, 323, 441, 296
    Scaled counts:       1, 1, 0, 1, 1, 2, 1.393
    Projected city loss: $774.79, $2,705.98, $0, $4,780.06,
                         $3,479.36, $29,017.88, $6,571.66
    Mean scaled count:   1.056
    Mean scaled dollars: $6,761.39

DISTRIBUTION TYPE DETERMINATION
--------------------------------
  Lower bound (American Samoa mean) = 0
  Upper bound (California mean)     = 1.056 ≈ 1 (nearest whole number)
  Integer values in range [0, 1]    = {0, 1} → BINARY distribution

  Binary probability:
    P(event = 1) = (lower_bound + upper_bound) / 2 = (0 + 1.056) / 2 = 0.528

MONTE CARLO SIMULATION — COUNT (BINARY)
----------------------------------------
  N = 10,000 iterations
  np.random.seed(42)
  mc_values = (np.random.random(10000) < 0.528).astype(int)
  → Count of 0 events: 4622  (46.2%)
  → Count of 1 event:  5378  (53.8%)

  Output figures:
    binary_ransomware_count.png  — bar chart of P(0) vs P(1)
    histogram_ransomware.png     — count histogram (0 or 1 events)
    count_ransomware_percentile.png — CDF/percentile chart

MONTE CARLO SIMULATION — IMPACT (NORMAL/UNIFORM)
-------------------------------------------------
  Impact lower bound: $0 (American Samoa mean)
  Impact upper bound: $6,761.39 (California mean)
  Model: Uniform distribution between $0 and $6,761.39
         (approximates a normal model with uniform prior over the observed range)

  np.random.seed(42)
  mc_impact = np.random.uniform(0, 6761.39, 10000)

  Resulting percentiles:
    10th percentile (90% chance cost ≥ this): $676.34
    50th percentile (50% chance cost ≥ this): $3,420.57
    90th percentile (10% chance cost ≥ this): $6,098.77
    80% confidence interval:                  [$676, $6,099]

  Output figures:
    histogram_ransomware_impact.png   — histogram of simulated costs
    percent_ransomware_impact.png     — CDF percentile chart of costs

GRAPH STYLE
-----------
  All graphs are produced in black and white:
    - Bar 0 (no-event): white fill, black edge
    - Bar 1 (event):    black fill, black edge
    - Background:       white
    - Grid lines:       gray dashed, alpha=0.5
    - Spines:           top and right removed

FIGURE DIMENSIONS
-----------------
  All figures: 1200 × 750 pixels at 100 dpi (12 × 7.5 inches)

REPRODUCTION SCRIPT
-------------------
  The complete reproduction script is located at:
    KandRStyle/research/risk_air_gap/generate_ransomware_figures.py

  To reproduce all figures from scratch:
    cd KandRStyle
    python3 research/risk_air_gap/generate_ransomware_figures.py

  This will overwrite the following files in KandRStyle/figures/:
    binary_ransomware_count.png
    histogram_ransomware.png
    histogram_ransomware_impact.png
    count_ransomware_percentile.png
    percent_ransomware_impact.png

NOTES ON EARLIER FIGURES
-------------------------
  The earlier ransomware figures (before Aug 2026) used a 50% binary
  probability, reflecting the raw Binary sheet default value of 0.5.
  The updated figures use 0.528 based on the mean of the American Samoa
  and California per-capita scaled counts (0 and 1.056 respectively).

RELATED FILES
-------------
  KandRStyle/excerpts/ransomware_section_filled.txt
    — LaTeX text for the Ransomware section of ut.tex (ready to insert)
  KandRStyle/research/risk_air_gap/ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED.xlsx
    — Source workbook; Binary_Ransomware sheet contains the Monte Carlo model
