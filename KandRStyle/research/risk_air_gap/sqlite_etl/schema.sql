PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    source_path TEXT NOT NULL UNIQUE,
    file_name TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    mime_type TEXT,
    size_bytes INTEGER,
    sha256 TEXT,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workbooks (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE REFERENCES sources(id) ON DELETE CASCADE,
    workbook_name TEXT NOT NULL,
    sheet_count INTEGER,
    defined_name_count INTEGER,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workbook_sheets (
    id INTEGER PRIMARY KEY,
    workbook_id INTEGER NOT NULL REFERENCES workbooks(id) ON DELETE CASCADE,
    sheet_index INTEGER NOT NULL,
    sheet_name TEXT NOT NULL,
    sheet_type TEXT NOT NULL,
    xml_path TEXT NOT NULL,
    dimension_ref TEXT,
    UNIQUE(workbook_id, sheet_index),
    UNIQUE(workbook_id, sheet_name)
);

CREATE TABLE IF NOT EXISTS workbook_defined_names (
    id INTEGER PRIMARY KEY,
    workbook_id INTEGER NOT NULL REFERENCES workbooks(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    local_sheet_id INTEGER NOT NULL DEFAULT -1,
    refers_to TEXT,
    UNIQUE(workbook_id, name, local_sheet_id)
);

CREATE TABLE IF NOT EXISTS workbook_sheet_relationships (
    id INTEGER PRIMARY KEY,
    sheet_id INTEGER NOT NULL REFERENCES workbook_sheets(id) ON DELETE CASCADE,
    rel_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    target TEXT NOT NULL,
    target_mode TEXT,
    UNIQUE(sheet_id, rel_id)
);

CREATE TABLE IF NOT EXISTS workbook_tables (
    id INTEGER PRIMARY KEY,
    sheet_id INTEGER NOT NULL REFERENCES workbook_sheets(id) ON DELETE CASCADE,
    table_name TEXT NOT NULL,
    display_name TEXT,
    ref TEXT NOT NULL,
    UNIQUE(sheet_id, table_name)
);

CREATE TABLE IF NOT EXISTS workbook_table_columns (
    id INTEGER PRIMARY KEY,
    table_id INTEGER NOT NULL REFERENCES workbook_tables(id) ON DELETE CASCADE,
    column_index INTEGER NOT NULL,
    column_name TEXT NOT NULL,
    UNIQUE(table_id, column_index)
);

CREATE TABLE IF NOT EXISTS workbook_merged_cells (
    id INTEGER PRIMARY KEY,
    sheet_id INTEGER NOT NULL REFERENCES workbook_sheets(id) ON DELETE CASCADE,
    merge_ref TEXT NOT NULL,
    UNIQUE(sheet_id, merge_ref)
);

CREATE TABLE IF NOT EXISTS workbook_cells (
    id INTEGER PRIMARY KEY,
    sheet_id INTEGER NOT NULL REFERENCES workbook_sheets(id) ON DELETE CASCADE,
    cell_ref TEXT NOT NULL,
    row_index INTEGER NOT NULL,
    column_index INTEGER NOT NULL,
    cell_type TEXT,
    raw_value TEXT,
    display_value TEXT,
    formula TEXT,
    formula_type TEXT,
    UNIQUE(sheet_id, cell_ref)
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY,
    workbook_id INTEGER NOT NULL REFERENCES workbooks(id) ON DELETE CASCADE,
    sheet_id INTEGER REFERENCES workbook_sheets(id) ON DELETE CASCADE,
    asset_kind TEXT NOT NULL,
    drawing_path TEXT,
    media_path TEXT,
    rel_id TEXT,
    anchor_kind TEXT,
    anchor_row INTEGER,
    anchor_column INTEGER,
    anchor_to_row INTEGER,
    anchor_to_column INTEGER,
    width_emu INTEGER,
    height_emu INTEGER,
    name TEXT,
    description TEXT,
    mime_type TEXT,
    extracted_path TEXT
);

CREATE TABLE IF NOT EXISTS geographies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    geography_type TEXT NOT NULL,
    parent_geography_id INTEGER REFERENCES geographies(id),
    usps_code TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    scenario_type TEXT NOT NULL,
    target_geography_id INTEGER REFERENCES geographies(id),
    benchmark_geography_id INTEGER REFERENCES geographies(id),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS crime_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normalized_name TEXT NOT NULL,
    group_name TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    unit TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    sheet_id INTEGER REFERENCES workbook_sheets(id) ON DELETE CASCADE,
    scenario_id INTEGER REFERENCES scenarios(id),
    geography_id INTEGER REFERENCES geographies(id),
    observation_year INTEGER,
    category_id INTEGER REFERENCES crime_categories(id),
    metric_id INTEGER NOT NULL REFERENCES metrics(id),
    value_numeric REAL,
    value_text TEXT,
    source_cell_ref TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS simulation_inputs (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    sheet_id INTEGER NOT NULL REFERENCES workbook_sheets(id) ON DELETE CASCADE,
    scenario_id INTEGER REFERENCES scenarios(id),
    geography_id INTEGER REFERENCES geographies(id),
    category_id INTEGER REFERENCES crime_categories(id),
    distribution_type TEXT NOT NULL,
    measure_type TEXT NOT NULL,
    confidence_level REAL,
    lower_bound REAL,
    upper_bound REAL,
    iteration_count INTEGER,
    value_range_ref TEXT,
    probability_range_ref TEXT,
    notes TEXT,
    UNIQUE(sheet_id)
);

CREATE TABLE IF NOT EXISTS simulation_outputs (
    id INTEGER PRIMARY KEY,
    simulation_input_id INTEGER NOT NULL REFERENCES simulation_inputs(id) ON DELETE CASCADE,
    output_name TEXT NOT NULL,
    output_value_numeric REAL,
    output_value_text TEXT,
    probability REAL,
    output_source TEXT NOT NULL,
    observation_year INTEGER,
    source_cell_ref TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS simulation_iterations (
    id INTEGER PRIMARY KEY,
    simulation_input_id INTEGER NOT NULL REFERENCES simulation_inputs(id) ON DELETE CASCADE,
    iteration_number INTEGER NOT NULL,
    iteration_value REAL NOT NULL,
    UNIQUE(simulation_input_id, iteration_number)
);

CREATE VIEW IF NOT EXISTS v_yearly_category_observations AS
SELECT
    o.observation_year,
    s.name AS scenario_name,
    g.name AS geography_name,
    bg.name AS benchmark_geography_name,
    c.name AS category_name,
    m.name AS metric_name,
    m.unit AS metric_unit,
    o.value_numeric,
    o.value_text,
    ws.sheet_name,
    o.source_cell_ref
FROM observations o
JOIN metrics m ON m.id = o.metric_id
LEFT JOIN crime_categories c ON c.id = o.category_id
LEFT JOIN geographies g ON g.id = o.geography_id
LEFT JOIN scenarios s ON s.id = o.scenario_id
LEFT JOIN geographies bg ON bg.id = s.benchmark_geography_id
LEFT JOIN workbook_sheets ws ON ws.id = o.sheet_id;

CREATE VIEW IF NOT EXISTS v_state_benchmark_comparison AS
SELECT
    observation_year,
    category_name,
    metric_name,
    MAX(CASE WHEN benchmark_geography_name = 'Tennessee' THEN value_numeric END) AS tennessee_value,
    MAX(CASE WHEN benchmark_geography_name = 'California' THEN value_numeric END) AS california_value,
    MAX(CASE WHEN benchmark_geography_name = 'American Samoa' THEN value_numeric END) AS american_samoa_value
FROM v_yearly_category_observations
WHERE metric_name IN ('victim_count', 'victim_impact_usd')
GROUP BY observation_year, category_name, metric_name;

CREATE VIEW IF NOT EXISTS v_simulation_summary AS
SELECT
    si.id AS simulation_id,
    ws.sheet_name,
    g.name AS geography_name,
    c.name AS category_name,
    si.distribution_type,
    si.measure_type,
    si.confidence_level,
    si.lower_bound,
    si.upper_bound,
    si.iteration_count,
    MAX(CASE WHEN so.output_name = 'minimum' AND so.output_source = 'computed_from_iterations' THEN so.output_value_numeric END) AS minimum_value,
    MAX(CASE WHEN so.output_name = 'mean' AND so.output_source = 'computed_from_iterations' THEN so.output_value_numeric END) AS mean_value,
    MAX(CASE WHEN so.output_name = 'median' AND so.output_source = 'computed_from_iterations' THEN so.output_value_numeric END) AS median_value,
    MAX(CASE WHEN so.output_name = 'maximum' AND so.output_source = 'computed_from_iterations' THEN so.output_value_numeric END) AS maximum_value,
    MAX(CASE WHEN so.output_name = 'sample_stddev' AND so.output_source = 'computed_from_iterations' THEN so.output_value_numeric END) AS sample_stddev,
    MAX(CASE WHEN so.output_name = 'percentile' AND so.probability = 0.05 AND so.output_source = 'workbook_percentile' THEN so.output_value_numeric END) AS workbook_p05,
    MAX(CASE WHEN so.output_name = 'percentile' AND so.probability = 0.50 AND so.output_source = 'workbook_percentile' THEN so.output_value_numeric END) AS workbook_p50,
    MAX(CASE WHEN so.output_name = 'percentile' AND so.probability = 0.95 AND so.output_source = 'workbook_percentile' THEN so.output_value_numeric END) AS workbook_p95
FROM simulation_inputs si
JOIN workbook_sheets ws ON ws.id = si.sheet_id
LEFT JOIN geographies g ON g.id = si.geography_id
LEFT JOIN crime_categories c ON c.id = si.category_id
LEFT JOIN simulation_outputs so ON so.simulation_input_id = si.id
GROUP BY si.id, ws.sheet_name, g.name, c.name, si.distribution_type, si.measure_type, si.confidence_level, si.lower_bound, si.upper_bound, si.iteration_count;

CREATE VIEW IF NOT EXISTS v_sheet_assets AS
SELECT
    ws.sheet_name,
    a.asset_kind,
    a.media_path,
    a.anchor_row,
    a.anchor_column,
    a.width_emu,
    a.height_emu,
    a.extracted_path
FROM assets a
LEFT JOIN workbook_sheets ws ON ws.id = a.sheet_id;
