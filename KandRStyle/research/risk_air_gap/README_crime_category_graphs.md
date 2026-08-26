# Crime Category Graph Generator

`generate_crime_category_graphs.py` builds black-and-white Monte Carlo figures and a filled section text file for any workbook crime category using NumPy.

## Requirements

- Python 3.10+
- `numpy`
- `matplotlib`
- `openpyxl`

Install:

```bash
pip install numpy matplotlib openpyxl
```

## Usage

```bash
python KandRStyle/research/risk_air_gap/generate_crime_category_graphs.py \
  --workbook KandRStyle/research/risk_air_gap/ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED.xlsx \
  --category IPR \
  --figures-dir KandRStyle/figures \
  --output-text KandRStyle/excerpts/ipr_section_filled.txt
```

## What it does

1. Reads 2016–2022 values from:
   - `City Summary AMERICAN_SAMOA`
   - `City Summary CALIFORNIA`
   - `City Summary Impact AMERICAN_SA`
   - `City Summary Impact CALIFORNIA`
2. Computes lower/upper means from American Samoa and California.
3. Chooses distribution type:
   - Binary when both means are between 0 and 1.
   - Discrete otherwise, with integer bins from floor(lower mean) to ceil(upper mean).
4. Runs 10,000 Monte Carlo iterations with NumPy.
5. Writes black-and-white figure files to `--figures-dir`.
6. Writes a filled template section to `--output-text` (does not modify `ut.tex`).

## Outputs

- `<binary|discrete>_<category>_count.png`
- `histogram_<category>_impact_bw.png`
- `percent_<category>_impact_bw.png`
- Filled text file at the `--output-text` path

## Notes

- The script treats spreadsheet error values (e.g., `#DIV/0!`) as `0`.
- Category aliases include `IPR`, `Intellectual Property Rights`, and `Intellectual Property Theft`.
