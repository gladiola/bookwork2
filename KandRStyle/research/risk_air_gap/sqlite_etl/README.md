# ComputerCrime workbook SQLite ETL

This folder implements the SQLite requirement for `/home/runner/work/bookwork2/bookwork2/KandRStyle/research/risk_air_gap/ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED.xlsx`.

## What it loads

- Raw workbook provenance into SQLite:
  - source files in `/home/runner/work/bookwork2/bookwork2/KandRStyle/research/risk_air_gap`
  - workbook sheets
  - defined names
  - sheet relationships
  - Excel tables and columns
  - merged cells
  - non-empty cells with formula text and stored values
- Clean analytical tables:
  - summary observations from the count and impact summary sheets
  - Monte Carlo scenario inputs from the `Uniform(...)` and `Normal(...)` sheets
  - Monte Carlo outputs derived from the cached 10,000 iteration values
  - embedded graph/image metadata from drawing relationships

## Sheet-to-table mapping

| Workbook content | SQLite tables |
| --- | --- |
| Workbook file inventory and nearby PDFs/CSVs/XLSX files | `sources`, `workbooks` |
| Sheet inventory and workbook structure | `workbook_sheets`, `workbook_defined_names`, `workbook_sheet_relationships`, `workbook_tables`, `workbook_table_columns`, `workbook_merged_cells`, `workbook_cells` |
| `State Summary Graphs`, `State Summary Graphs CALIFORNIA`, `Summary Graphs AMERICAN_SAMOA` | `observations` with metric `victim_count` |
| `City Summary Impact`, `City Summary Impact CALIFORNIA`, `City Summary Impact AMERICAN_SA` | `observations` with metric `victim_impact_usd` plus helper population metrics |
| `Uniform(#/$) ...`, `Normal(#/$) ...` | `simulation_inputs`, `simulation_outputs`, optional `simulation_iterations` |
| Embedded images and chart assets, including `Box_Tennessee`, `Box_California`, `Box_American_Samoa` | `assets` |

## Graph handling

Graphs are stored as assets, not reverse-engineered into primary fact tables.

- The ETL records sheet name, drawing path, media path, anchor position, and image size in `assets`.
- If `--extract-assets-dir` is supplied, the workbook PNGs are also written out to disk.
- The numeric values behind the summary graphs are loaded into `observations` from the summary sheets.

## Monte Carlo handling

Monte Carlo sheets are loaded in two layers.

- Inputs: distribution type, measure type, confidence level, lower bound, upper bound, and iteration range go into `simulation_inputs`.
- Outputs: min, max, mean, median, sample standard deviation, and selected percentiles go into `simulation_outputs`.
- The workbook already stores cached random samples in column `D`; the ETL computes summary statistics from those cached values.
- If full reproducibility at the row level is needed, pass `--include-iterations` to load the 10,000 iteration values into `simulation_iterations`.

## Usage

```bash
python /home/runner/work/bookwork2/bookwork2/KandRStyle/research/risk_air_gap/sqlite_etl/build_computercrime_sqlite.py \
  --sqlite /tmp/computercrime.sqlite3 \
  --extract-assets-dir /tmp/computercrime-assets
```

To include all Monte Carlo iterations:

```bash
python /home/runner/work/bookwork2/bookwork2/KandRStyle/research/risk_air_gap/sqlite_etl/build_computercrime_sqlite.py \
  --sqlite /tmp/computercrime.sqlite3 \
  --extract-assets-dir /tmp/computercrime-assets \
  --include-iterations
```

## Useful views

- `v_yearly_category_observations`
- `v_state_benchmark_comparison`
- `v_simulation_summary`
- `v_sheet_assets`
