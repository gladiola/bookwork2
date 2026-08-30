# Conditional Framework Findings (AS<TN Screen)

This summary matches the LaTeX file:

- `/home/runner/work/bookwork2/bookwork2/KandRStyle/research/risk_air_gap/conditional_framework_findings.tex`

## Rule applied

1. Screen categories using adjusted per-capita count means where `AS < TN`.
2. Keep only those categories for follow-on analysis.
3. Use the same retained set for both count and impact ANOVA.

## Retained categories (count screen passed)

- Personal Data Breach
- Phishing
- Ransomware
- Extortion
- IPR/Counterfeit
- Identity Theft
- BEC

## Excluded categories (count screen failed)

- Data Breach
- Malware
- Crimes Against Children
- Threats/Stalking/Harassment/Terrorism

## Statistical outcomes at alpha = 0.05

- Count ANOVA (full 11 categories): `p = 0.08` -> fail
- Impact ANOVA (full 11 categories): `p = 0.36` -> fail
- Count ANOVA (retained 7 categories): `p = 0.0387` -> pass
- Impact ANOVA (same retained 7 categories): `p = 0.2695` -> fail

## Practical reading

- The conditional framework is statistically supportable for **count** in the retained subset.
- The same framework remains unsupported for **impact** by p-value.
