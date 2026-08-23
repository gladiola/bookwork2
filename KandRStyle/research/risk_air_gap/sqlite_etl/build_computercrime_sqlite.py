from __future__ import annotations

import argparse
import hashlib
import mimetypes
import re
import sqlite3
import statistics
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET
from zipfile import ZipFile

NS_MAIN = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
NS_DOCREL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS_PKGREL = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS_DRAWING = 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing'
NS_DRAWING_MAIN = 'http://schemas.openxmlformats.org/drawingml/2006/main'

DEFAULT_WORKBOOK = (
    Path(__file__).resolve().parent.parent
    / 'ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED.xlsx'
)
DEFAULT_SOURCE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = Path(__file__).resolve().with_name('schema.sql')
DEFAULT_SQLITE = Path(__file__).resolve().with_name('computercrime.sqlite3')

def column_letters_to_index(letters: str) -> int:
    value = 0
    for char in letters:
        value = (value * 26) + (ord(char.upper()) - 64)
    return value


def column_index_to_letters(index: int) -> str:
    letters: list[str] = []
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters.append(chr(65 + remainder))
    return ''.join(reversed(letters))


def split_cell_reference(cell_ref: str) -> tuple[int, int]:
    match = re.fullmatch(r'([A-Z]+)(\d+)', cell_ref)
    if not match:
        raise ValueError(f'Unsupported cell reference: {cell_ref}')
    return int(match.group(2)), column_letters_to_index(match.group(1))


SUMMARY_SPECS = [
    {
        'sheet_name': 'State Summary Graphs',
        'scenario_name': 'Chattanooga scaled from Tennessee IC3',
        'benchmark_name': 'Tennessee',
        'benchmark_type': 'state',
        'metric_name': 'victim_count',
        'metric_unit': 'count',
        'header_row': 4,
        'group_row': 3,
        'year_rows': range(5, 12),
        'population_column': 'C',
        'metric_columns': range(column_letters_to_index('G'), column_letters_to_index('R') + 1),
    },
    {
        'sheet_name': 'State Summary Graphs CALIFORNIA',
        'scenario_name': 'Chattanooga scaled from California IC3',
        'benchmark_name': 'California',
        'benchmark_type': 'state',
        'metric_name': 'victim_count',
        'metric_unit': 'count',
        'header_row': 4,
        'group_row': 3,
        'year_rows': range(5, 12),
        'population_column': 'C',
        'metric_columns': range(column_letters_to_index('G'), column_letters_to_index('R') + 1),
    },
    {
        'sheet_name': 'Summary Graphs AMERICAN_SAMOA',
        'scenario_name': 'Chattanooga scaled from American Samoa IC3',
        'benchmark_name': 'American Samoa',
        'benchmark_type': 'territory',
        'metric_name': 'victim_count',
        'metric_unit': 'count',
        'header_row': 4,
        'group_row': 3,
        'year_rows': range(5, 12),
        'population_column': 'C',
        'metric_columns': range(column_letters_to_index('G'), column_letters_to_index('R') + 1),
    },
    {
        'sheet_name': 'City Summary Impact',
        'scenario_name': 'Chattanooga impact scaled from Tennessee IC3',
        'benchmark_name': 'Tennessee',
        'benchmark_type': 'state',
        'metric_name': 'victim_impact_usd',
        'metric_unit': 'usd',
        'header_row': 4,
        'group_row': 3,
        'year_rows': range(5, 12),
        'population_column': 'C',
        'metric_columns': range(column_letters_to_index('F'), column_letters_to_index('P') + 1),
        'extra_rows': {
            14: 'average_population_deviation',
            15: 'projected_population',
            16: 'projected_population_high',
            17: 'projected_population_low',
        },
    },
    {
        'sheet_name': 'City Summary Impact CALIFORNIA',
        'scenario_name': 'Chattanooga impact scaled from California IC3',
        'benchmark_name': 'California',
        'benchmark_type': 'state',
        'metric_name': 'victim_impact_usd',
        'metric_unit': 'usd',
        'header_row': 4,
        'group_row': 3,
        'year_rows': range(5, 12),
        'population_column': 'C',
        'metric_columns': range(column_letters_to_index('F'), column_letters_to_index('P') + 1),
        'extra_rows': {
            14: 'average_population_deviation',
            15: 'projected_population',
            16: 'projected_population_high',
            17: 'projected_population_low',
        },
    },
    {
        'sheet_name': 'City Summary Impact AMERICAN_SA',
        'scenario_name': 'Chattanooga impact scaled from American Samoa IC3',
        'benchmark_name': 'American Samoa',
        'benchmark_type': 'territory',
        'metric_name': 'victim_impact_usd',
        'metric_unit': 'usd',
        'header_row': 4,
        'group_row': 3,
        'year_rows': range(5, 12),
        'population_column': 'C',
        'metric_columns': range(column_letters_to_index('F'), column_letters_to_index('P') + 1),
        'extra_rows': {
            14: 'average_population_deviation',
            15: 'projected_population',
            16: 'projected_population_high',
            17: 'projected_population_low',
        },
    },
]

SIMULATION_PROBABILITY_ROWS = range(21, 26)
TARGET_CITY = 'Chattanooga, Tennessee'


def normalized_category_name(name: str) -> str:
    text = name.strip().lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')


def detect_sheet_type(sheet_name: str) -> str:
    if sheet_name == 'Table of Contents':
        return 'lookup_sheet'
    if sheet_name.startswith(('Uniform(', 'Normal(')):
        return 'simulation_sheet'
    if sheet_name.startswith('Box_'):
        return 'chart_output_sheet'
    if 'Summary Graphs' in sheet_name or sheet_name.startswith('City Summary'):
        return 'summary_sheet'
    if sheet_name.startswith('Discrete') or sheet_name == 'Binary':
        return 'simulation_template_sheet'
    if 'IC3' in sheet_name:
        return 'source_data_sheet'
    return 'worksheet'


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def guess_source_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == '.xlsx':
        return 'xlsx'
    if suffix == '.csv':
        return 'csv'
    if suffix == '.pdf':
        return 'pdf'
    return suffix.lstrip('.') or 'file'


def sqlite_connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def apply_schema(connection: sqlite3.Connection, schema_path: Path) -> None:
    connection.executescript(schema_path.read_text(encoding='utf-8'))


def upsert_source(connection: sqlite3.Connection, file_path: Path) -> int:
    mime_type = mimetypes.guess_type(file_path.name)[0]
    connection.execute(
        '''
        INSERT INTO sources (source_path, file_name, source_kind, mime_type, size_bytes, sha256)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_path) DO UPDATE SET
            file_name = excluded.file_name,
            source_kind = excluded.source_kind,
            mime_type = excluded.mime_type,
            size_bytes = excluded.size_bytes,
            sha256 = excluded.sha256,
            imported_at = CURRENT_TIMESTAMP
        ''',
        (
            str(file_path),
            file_path.name,
            guess_source_kind(file_path),
            mime_type,
            file_path.stat().st_size,
            sha256_file(file_path),
        ),
    )
    return connection.execute(
        'SELECT id FROM sources WHERE source_path = ?',
        (str(file_path),),
    ).fetchone()['id']


def inventory_source_directory(connection: sqlite3.Connection, source_dir: Path, excluded_dir: Path) -> None:
    for path in sorted(source_dir.iterdir()):
        if path.name.startswith('~$'):
            continue
        if path == excluded_dir or path.name == excluded_dir.name:
            continue
        if path.is_file():
            upsert_source(connection, path)


def parse_relationships(xml_bytes: bytes) -> dict[str, dict[str, str]]:
    root = ET.fromstring(xml_bytes)
    relationships: dict[str, dict[str, str]] = {}
    for relationship in root:
        relationships[relationship.attrib['Id']] = {
            'Type': relationship.attrib.get('Type', ''),
            'Target': relationship.attrib.get('Target', ''),
            'TargetMode': relationship.attrib.get('TargetMode', ''),
        }
    return relationships


def load_shared_strings(zf: ZipFile) -> list[str]:
    if 'xl/sharedStrings.xml' not in zf.namelist():
        return []
    root = ET.fromstring(zf.read('xl/sharedStrings.xml'))
    values: list[str] = []
    for shared in root:
        values.append(''.join(node.text or '' for node in shared.iter(f'{{{NS_MAIN}}}t')))
    return values


def decode_inline_string(cell: ET.Element) -> str:
    return ''.join(node.text or '' for node in cell.iter(f'{{{NS_MAIN}}}t'))


def decode_cell_value(cell: ET.Element, shared_strings: list[str]) -> str | None:
    cell_type = cell.attrib.get('t')
    value_node = cell.find(f'{{{NS_MAIN}}}v')
    if cell_type == 'inlineStr':
        return decode_inline_string(cell)
    if cell_type == 's' and value_node is not None and value_node.text is not None:
        return shared_strings[int(value_node.text)]
    if value_node is not None:
        return value_node.text
    return None


def iter_sheet_cells(sheet_xml: bytes, shared_strings: list[str]) -> Iterable[dict[str, str | int | None]]:
    root = ET.fromstring(sheet_xml)
    sheet_data = root.find(f'{{{NS_MAIN}}}sheetData')
    if sheet_data is None:
        return []
    rows: list[dict[str, str | int | None]] = []
    for row in sheet_data:
        for cell in row:
            cell_ref = cell.attrib.get('r')
            if not cell_ref:
                continue
            row_index, column_index = split_cell_reference(cell_ref)
            formula = cell.find(f'{{{NS_MAIN}}}f')
            decoded_value = decode_cell_value(cell, shared_strings)
            rows.append(
                {
                    'cell_ref': cell_ref,
                    'row_index': row_index,
                    'column_index': column_index,
                    'cell_type': cell.attrib.get('t', 'n'),
                    'raw_value': decoded_value,
                    'display_value': decoded_value,
                    'formula': formula.text if formula is not None else None,
                    'formula_type': formula.attrib.get('t') if formula is not None else None,
                }
            )
    return rows


def load_sheet_value_map(zf: ZipFile, xml_path: str, shared_strings: list[str]) -> dict[str, str]:
    value_map: dict[str, str] = {}
    for cell in iter_sheet_cells(zf.read(xml_path), shared_strings):
        if cell['display_value'] is not None:
            value_map[str(cell['cell_ref'])] = str(cell['display_value'])
    return value_map


def sheet_relationship_path(xml_path: str) -> str:
    return xml_path.replace('xl/worksheets/', 'xl/worksheets/_rels/') + '.rels'


def drawing_relationship_path(drawing_path: str) -> str:
    drawing_name = Path(drawing_path).name
    return f'xl/drawings/_rels/{drawing_name}.rels'


def workbook_target_to_part(target: str) -> str:
    if target.startswith('/'):
        return target.lstrip('/')
    return f'xl/{target.lstrip("/")}'


def extract_tables(
    connection: sqlite3.Connection,
    zf: ZipFile,
    sheet_id: int,
    sheet_relations: dict[str, dict[str, str]],
) -> None:
    for relation in sheet_relations.values():
        if not relation['Type'].endswith('/table'):
            continue
        table_part = workbook_target_to_part(relation['Target'])
        root = ET.fromstring(zf.read(table_part))
        connection.execute(
            '''
            INSERT INTO workbook_tables (sheet_id, table_name, display_name, ref)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(sheet_id, table_name) DO UPDATE SET
                display_name = excluded.display_name,
                ref = excluded.ref
            ''',
            (
                sheet_id,
                root.attrib['name'],
                root.attrib.get('displayName'),
                root.attrib['ref'],
            ),
        )
        table_id = connection.execute(
            'SELECT id FROM workbook_tables WHERE sheet_id = ? AND table_name = ?',
            (sheet_id, root.attrib['name']),
        ).fetchone()['id']
        columns = root.find(f'{{{NS_MAIN}}}tableColumns')
        if columns is None:
            continue
        for index, column in enumerate(columns, start=1):
            connection.execute(
                '''
                INSERT INTO workbook_table_columns (table_id, column_index, column_name)
                VALUES (?, ?, ?)
                ON CONFLICT(table_id, column_index) DO UPDATE SET
                    column_name = excluded.column_name
                ''',
                (table_id, index, column.attrib.get('name', f'Column{index}')),
            )


def extract_assets(
    connection: sqlite3.Connection,
    zf: ZipFile,
    workbook_id: int,
    sheet_id: int,
    sheet_relations: dict[str, dict[str, str]],
    extract_dir: Path | None,
    sheet_name: str,
) -> None:
    drawing_relations = {
        rel_id: relation for rel_id, relation in sheet_relations.items() if relation['Type'].endswith('/drawing')
    }
    for rel_id, relation in drawing_relations.items():
        drawing_part = workbook_target_to_part(relation['Target'])
        drawing_root = ET.fromstring(zf.read(drawing_part))
        media_relations: dict[str, dict[str, str]] = {}
        drawing_rel_path = drawing_relationship_path(drawing_part)
        if drawing_rel_path in zf.namelist():
            media_relations = parse_relationships(zf.read(drawing_rel_path))
        for anchor in drawing_root:
            anchor_kind = anchor.tag.split('}')[-1]
            from_node = anchor.find(f'{{{NS_DRAWING}}}from')
            to_node = anchor.find(f'{{{NS_DRAWING}}}to')
            pic = anchor.find(f'{{{NS_DRAWING}}}pic')
            if from_node is None or pic is None:
                continue
            blip = pic.find(f'.//{{{NS_DRAWING_MAIN}}}blip')
            if blip is None:
                continue
            image_rel_id = blip.attrib.get(f'{{{NS_DOCREL}}}embed')
            if not image_rel_id:
                continue
            image_relation = media_relations.get(image_rel_id, {})
            media_path = workbook_target_to_part(image_relation.get('Target', '')) if image_relation else None
            extracted_path = None
            if extract_dir is not None and media_path:
                sheet_dir = extract_dir / sanitize_path_component(sheet_name)
                sheet_dir.mkdir(parents=True, exist_ok=True)
                target_name = f'{int(from_node.findtext(f"{{{NS_DRAWING}}}row", default="0")) + 1:04d}_{Path(media_path).name}'
                target_path = sheet_dir / target_name
                target_path.write_bytes(zf.read(media_path))
                extracted_path = str(target_path)
            name_node = pic.find(f'.//{{{NS_DRAWING}}}cNvPr')
            ext_node = anchor.find(f'{{{NS_DRAWING}}}ext')
            connection.execute(
                '''
                INSERT INTO assets (
                    workbook_id, sheet_id, asset_kind, drawing_path, media_path, rel_id,
                    anchor_kind, anchor_row, anchor_column, anchor_to_row, anchor_to_column,
                    width_emu, height_emu, name, description, mime_type, extracted_path
                )
                VALUES (?, ?, 'image', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    workbook_id,
                    sheet_id,
                    drawing_part,
                    media_path,
                    image_rel_id,
                    anchor_kind,
                    int(from_node.findtext(f'{{{NS_DRAWING}}}row', default='0')) + 1,
                    int(from_node.findtext(f'{{{NS_DRAWING}}}col', default='0')) + 1,
                    int(to_node.findtext(f'{{{NS_DRAWING}}}row', default='0')) + 1 if to_node is not None else None,
                    int(to_node.findtext(f'{{{NS_DRAWING}}}col', default='0')) + 1 if to_node is not None else None,
                    int(ext_node.attrib.get('cx', '0')) if ext_node is not None else None,
                    int(ext_node.attrib.get('cy', '0')) if ext_node is not None else None,
                    name_node.attrib.get('name') if name_node is not None else None,
                    name_node.attrib.get('descr') if name_node is not None else None,
                    mimetypes.guess_type(media_path or '')[0],
                    extracted_path,
                ),
            )


def sanitize_path_component(text: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]+', '_', text).strip('_') or 'sheet'


def ensure_geography(
    connection: sqlite3.Connection,
    name: str,
    geography_type: str,
    parent_name: str | None = None,
    usps_code: str | None = None,
    notes: str | None = None,
) -> int:
    parent_id = None
    if parent_name is not None:
        parent = connection.execute('SELECT id FROM geographies WHERE name = ?', (parent_name,)).fetchone()
        parent_id = parent['id'] if parent else None
    connection.execute(
        '''
        INSERT INTO geographies (name, geography_type, parent_geography_id, usps_code, notes)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            geography_type = excluded.geography_type,
            parent_geography_id = COALESCE(geographies.parent_geography_id, excluded.parent_geography_id),
            usps_code = COALESCE(geographies.usps_code, excluded.usps_code),
            notes = COALESCE(geographies.notes, excluded.notes)
        ''',
        (name, geography_type, parent_id, usps_code, notes),
    )
    return connection.execute('SELECT id FROM geographies WHERE name = ?', (name,)).fetchone()['id']


def ensure_scenario(
    connection: sqlite3.Connection,
    name: str,
    scenario_type: str,
    target_geography_id: int | None,
    benchmark_geography_id: int | None,
    notes: str | None = None,
) -> int:
    connection.execute(
        '''
        INSERT INTO scenarios (name, scenario_type, target_geography_id, benchmark_geography_id, notes)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            scenario_type = excluded.scenario_type,
            target_geography_id = COALESCE(scenarios.target_geography_id, excluded.target_geography_id),
            benchmark_geography_id = COALESCE(scenarios.benchmark_geography_id, excluded.benchmark_geography_id),
            notes = COALESCE(scenarios.notes, excluded.notes)
        ''',
        (name, scenario_type, target_geography_id, benchmark_geography_id, notes),
    )
    return connection.execute('SELECT id FROM scenarios WHERE name = ?', (name,)).fetchone()['id']


def ensure_metric(connection: sqlite3.Connection, name: str, unit: str, description: str) -> int:
    connection.execute(
        '''
        INSERT INTO metrics (name, unit, description)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            unit = excluded.unit,
            description = excluded.description
        ''',
        (name, unit, description),
    )
    return connection.execute('SELECT id FROM metrics WHERE name = ?', (name,)).fetchone()['id']


def ensure_category(connection: sqlite3.Connection, name: str, group_name: str | None = None) -> int:
    connection.execute(
        '''
        INSERT INTO crime_categories (name, normalized_name, group_name)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            normalized_name = excluded.normalized_name,
            group_name = COALESCE(crime_categories.group_name, excluded.group_name)
        ''',
        (name, normalized_category_name(name), group_name),
    )
    return connection.execute('SELECT id FROM crime_categories WHERE name = ?', (name,)).fetchone()['id']


def try_float(value: str | None) -> float | None:
    if value is None or value == '':
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_group_labels(value_map: dict[str, str], row_index: int, metric_columns: Iterable[int]) -> dict[int, str | None]:
    groups: dict[int, str | None] = {}
    current_group: str | None = None
    for column_index in metric_columns:
        ref = f'{column_index_to_letters(column_index)}{row_index}'
        if ref in value_map and value_map[ref].strip():
            current_group = value_map[ref].strip()
        groups[column_index] = current_group
    return groups


def extract_summary_observations(
    connection: sqlite3.Connection,
    zf: ZipFile,
    workbook_source_id: int,
    sheet_ids_by_name: dict[str, int],
    xml_by_sheet_name: dict[str, str],
    shared_strings: list[str],
) -> None:
    city_id = ensure_geography(connection, TARGET_CITY, 'city', parent_name='Tennessee', notes='Target city population used throughout workbook summary sheets.')
    for spec in SUMMARY_SPECS:
        sheet_id = sheet_ids_by_name.get(spec['sheet_name'])
        xml_path = xml_by_sheet_name.get(spec['sheet_name'])
        if sheet_id is None or xml_path is None:
            continue
        benchmark_id = ensure_geography(
            connection,
            spec['benchmark_name'],
            spec['benchmark_type'],
            notes='Benchmark geography referenced by the workbook summary sheets.',
        )
        scenario_id = ensure_scenario(
            connection,
            spec['scenario_name'],
            'scaled_benchmark_to_city',
            city_id,
            benchmark_id,
            notes='Workbook summary sheet scales benchmark IC3 rates to the Chattanooga population.',
        )
        metric_id = ensure_metric(
            connection,
            spec['metric_name'],
            spec['metric_unit'],
            'Summary observation extracted from workbook summary sheets.',
        )
        population_metric_id = ensure_metric(
            connection,
            'population',
            'people',
            'Population value carried on summary sheets.',
        )
        value_map = load_sheet_value_map(zf, xml_path, shared_strings)
        group_map = parse_group_labels(value_map, spec['group_row'], spec['metric_columns'])
        population_column = spec['population_column']
        for row_index in spec['year_rows']:
            year = int(float(value_map[f'B{row_index}']))
            population_value = try_float(value_map.get(f'{population_column}{row_index}'))
            connection.execute(
                '''
                INSERT INTO observations (
                    source_id, sheet_id, scenario_id, geography_id, observation_year,
                    category_id, metric_id, value_numeric, value_text, source_cell_ref, notes
                ) VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?)
                ''',
                (
                    workbook_source_id,
                    sheet_id,
                    scenario_id,
                    city_id,
                    year,
                    population_metric_id,
                    population_value,
                    value_map.get(f'{population_column}{row_index}'),
                    f'{population_column}{row_index}',
                    'Population value copied from summary sheet.',
                ),
            )
            for column_index in spec['metric_columns']:
                header_ref = f'{column_index_to_letters(column_index)}{spec["header_row"]}'
                header = value_map.get(header_ref)
                if not header or header.startswith('Column'):
                    continue
                value_ref = f'{column_index_to_letters(column_index)}{row_index}'
                raw_value = value_map.get(value_ref)
                category_id = ensure_category(connection, header, group_map.get(column_index))
                connection.execute(
                    '''
                    INSERT INTO observations (
                        source_id, sheet_id, scenario_id, geography_id, observation_year,
                        category_id, metric_id, value_numeric, value_text, source_cell_ref, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        workbook_source_id,
                        sheet_id,
                        scenario_id,
                        city_id,
                        year,
                        category_id,
                        metric_id,
                        try_float(raw_value),
                        raw_value,
                        value_ref,
                        f'Benchmark scenario based on {spec["benchmark_name"]}.',
                    ),
                )
        for extra_row, metric_name in spec.get('extra_rows', {}).items():
            metric = ensure_metric(connection, metric_name, 'people', 'Population helper value carried on impact summary sheets.')
            raw_value = value_map.get(f'D{extra_row}')
            connection.execute(
                '''
                INSERT INTO observations (
                    source_id, sheet_id, scenario_id, geography_id, observation_year,
                    category_id, metric_id, value_numeric, value_text, source_cell_ref, notes
                ) VALUES (?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, ?)
                ''',
                (
                    workbook_source_id,
                    sheet_id,
                    scenario_id,
                    city_id,
                    metric,
                    try_float(raw_value),
                    raw_value,
                    f'D{extra_row}',
                    'Sheet-level helper value extracted from impact summary sheet.',
                ),
            )


def percentile_inc(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError('Cannot compute percentile for empty data set.')
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    rank = (len(ordered) - 1) * probability
    lower_index = int(rank)
    upper_index = min(lower_index + 1, len(ordered) - 1)
    fraction = rank - lower_index
    lower = ordered[lower_index]
    upper = ordered[upper_index]
    return lower + (upper - lower) * fraction


def parse_simulation_sheet_name(sheet_name: str) -> tuple[str, str, str]:
    if sheet_name.startswith('Uniform('):
        distribution = 'uniform'
    elif sheet_name.startswith('Normal('):
        distribution = 'normal'
    else:
        distribution = 'unknown'
    measure_type = 'victim_count' if '(#)' in sheet_name else 'victim_impact_usd'
    category = sheet_name.split(') ', 1)[1].strip()
    return distribution, measure_type, category


def extract_simulations(
    connection: sqlite3.Connection,
    zf: ZipFile,
    workbook_source_id: int,
    sheet_ids_by_name: dict[str, int],
    xml_by_sheet_name: dict[str, str],
    shared_strings: list[str],
    include_iterations: bool,
) -> None:
    city_id = ensure_geography(connection, TARGET_CITY, 'city', parent_name='Tennessee', notes='Target city population used throughout workbook summary sheets.')
    tennessee_id = ensure_geography(connection, 'Tennessee', 'state', notes='Benchmark state for the workbook simulation sheets.')
    scenario_id = ensure_scenario(
        connection,
        'Monte Carlo scenarios from Tennessee workbook projections',
        'monte_carlo',
        city_id,
        tennessee_id,
        notes='Workbook contains one set of Monte Carlo simulation sheets; they are treated as Tennessee-derived city projections.',
    )
    for sheet_name, xml_path in xml_by_sheet_name.items():
        if not sheet_name.startswith(('Uniform(', 'Normal(')):
            continue
        sheet_id = sheet_ids_by_name[sheet_name]
        value_map = load_sheet_value_map(zf, xml_path, shared_strings)
        distribution_type, measure_type, category_name = parse_simulation_sheet_name(sheet_name)
        metric_unit = 'count' if measure_type == 'victim_count' else 'usd'
        ensure_metric(connection, measure_type, metric_unit, 'Monte Carlo sheet measure type.')
        category_id = ensure_category(connection, category_name)
        lower_bound = try_float(value_map.get('C7'))
        upper_bound = try_float(value_map.get('C5'))
        confidence_text = value_map.get('B4', '')
        confidence_level = None
        confidence_match = re.search(r'(\d+(?:\.\d+)?)%', confidence_text)
        if confidence_match:
            confidence_level = float(confidence_match.group(1)) / 100.0
        iteration_values: list[tuple[int, float]] = []
        for cell_ref, raw_value in value_map.items():
            if not cell_ref.startswith('D'):
                continue
            row_index, _ = split_cell_reference(cell_ref)
            if 21 <= row_index <= 10020:
                numeric_value = try_float(raw_value)
                if numeric_value is not None:
                    iteration_values.append((row_index - 20, numeric_value))
        iteration_values.sort(key=lambda item: item[0])
        numeric_values = [value for _, value in iteration_values]
        connection.execute(
            '''
            INSERT INTO simulation_inputs (
                source_id, sheet_id, scenario_id, geography_id, category_id,
                distribution_type, measure_type, confidence_level, lower_bound,
                upper_bound, iteration_count, value_range_ref, probability_range_ref, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sheet_id) DO UPDATE SET
                scenario_id = excluded.scenario_id,
                geography_id = excluded.geography_id,
                category_id = excluded.category_id,
                distribution_type = excluded.distribution_type,
                measure_type = excluded.measure_type,
                confidence_level = excluded.confidence_level,
                lower_bound = excluded.lower_bound,
                upper_bound = excluded.upper_bound,
                iteration_count = excluded.iteration_count,
                value_range_ref = excluded.value_range_ref,
                probability_range_ref = excluded.probability_range_ref,
                notes = excluded.notes
            ''',
            (
                workbook_source_id,
                sheet_id,
                scenario_id,
                city_id,
                category_id,
                distribution_type,
                measure_type,
                confidence_level,
                lower_bound,
                upper_bound,
                len(numeric_values),
                'D21:D10020',
                'N21:O25',
                'Monte Carlo sheet values extracted from cached random samples stored in the workbook.',
            ),
        )
        simulation_input_id = connection.execute(
            'SELECT id FROM simulation_inputs WHERE sheet_id = ?',
            (sheet_id,),
        ).fetchone()['id']
        connection.execute('DELETE FROM simulation_outputs WHERE simulation_input_id = ?', (simulation_input_id,))
        if include_iterations:
            connection.execute('DELETE FROM simulation_iterations WHERE simulation_input_id = ?', (simulation_input_id,))
        if not numeric_values:
            continue
        computed_outputs = {
            'minimum': min(numeric_values),
            'maximum': max(numeric_values),
            'mean': statistics.mean(numeric_values),
            'median': statistics.median(numeric_values),
            'sample_stddev': statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0,
            'percentile_05': percentile_inc(numeric_values, 0.05),
            'percentile_10': percentile_inc(numeric_values, 0.10),
            'percentile_90': percentile_inc(numeric_values, 0.90),
            'percentile_95': percentile_inc(numeric_values, 0.95),
        }
        for output_name, output_value in computed_outputs.items():
            probability = None
            if output_name.startswith('percentile_'):
                probability = float(output_name.split('_')[1]) / 100.0
            connection.execute(
                '''
                INSERT INTO simulation_outputs (
                    simulation_input_id, output_name, output_value_numeric, output_value_text,
                    probability, output_source, observation_year, source_cell_ref, notes
                ) VALUES (?, ?, ?, ?, ?, 'computed_from_iterations', NULL, NULL, 'Computed from cached iteration values stored in column D.')
                ''',
                (
                    simulation_input_id,
                    'percentile' if probability is not None else output_name,
                    output_value,
                    str(output_value),
                    probability,
                ),
            )
        for row_index in SIMULATION_PROBABILITY_ROWS:
            probability = try_float(value_map.get(f'N{row_index}'))
            output_value = try_float(value_map.get(f'O{row_index}'))
            if probability is None or output_value is None:
                continue
            connection.execute(
                '''
                INSERT INTO simulation_outputs (
                    simulation_input_id, output_name, output_value_numeric, output_value_text,
                    probability, output_source, observation_year, source_cell_ref, notes
                ) VALUES (?, 'percentile', ?, ?, ?, 'workbook_percentile', NULL, ?, 'Workbook percentile point copied from the probability table.')
                ''',
                (
                    simulation_input_id,
                    output_value,
                    value_map.get(f'O{row_index}'),
                    probability,
                    f'O{row_index}',
                ),
            )
        if include_iterations:
            connection.executemany(
                'INSERT INTO simulation_iterations (simulation_input_id, iteration_number, iteration_value) VALUES (?, ?, ?)',
                [(simulation_input_id, iteration_number, iteration_value) for iteration_number, iteration_value in iteration_values],
            )


def seed_geographies(connection: sqlite3.Connection) -> None:
    ensure_geography(connection, 'United States', 'country', usps_code='US')
    ensure_geography(connection, 'Tennessee', 'state', parent_name='United States', usps_code='TN')
    ensure_geography(connection, 'California', 'state', parent_name='United States', usps_code='CA')
    ensure_geography(connection, 'American Samoa', 'territory', parent_name='United States', usps_code='AS')
    ensure_geography(connection, TARGET_CITY, 'city', parent_name='Tennessee', notes='Target city population used throughout workbook summary sheets.')


def import_workbook_package(
    connection: sqlite3.Connection,
    workbook_path: Path,
    extract_dir: Path | None,
) -> tuple[int, int, dict[str, int], dict[str, str], list[str]]:
    source_id = upsert_source(connection, workbook_path)
    with ZipFile(workbook_path) as zf:
        shared_strings = load_shared_strings(zf)
        workbook_root = ET.fromstring(zf.read('xl/workbook.xml'))
        workbook_relations = parse_relationships(zf.read('xl/_rels/workbook.xml.rels'))
        sheets_root = workbook_root.find(f'{{{NS_MAIN}}}sheets')
        defined_names_root = workbook_root.find(f'{{{NS_MAIN}}}definedNames')
        defined_name_count = len(list(defined_names_root)) if defined_names_root is not None else 0
        sheet_count = len(list(sheets_root)) if sheets_root is not None else 0
        connection.execute(
            '''
            INSERT INTO workbooks (source_id, workbook_name, sheet_count, defined_name_count)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source_id) DO UPDATE SET
                workbook_name = excluded.workbook_name,
                sheet_count = excluded.sheet_count,
                defined_name_count = excluded.defined_name_count,
                imported_at = CURRENT_TIMESTAMP
            ''',
            (source_id, workbook_path.name, sheet_count, defined_name_count),
        )
        workbook_id = connection.execute(
            'SELECT id FROM workbooks WHERE source_id = ?',
            (source_id,),
        ).fetchone()['id']
        connection.execute('DELETE FROM workbook_defined_names WHERE workbook_id = ?', (workbook_id,))
        if defined_names_root is not None:
            for defined_name in defined_names_root:
                connection.execute(
                    '''
                    INSERT INTO workbook_defined_names (workbook_id, name, local_sheet_id, refers_to)
                    VALUES (?, ?, ?, ?)
                    ''',
                    (
                        workbook_id,
                        defined_name.attrib.get('name', ''),
                        int(defined_name.attrib['localSheetId']) if 'localSheetId' in defined_name.attrib else -1,
                        defined_name.text,
                    ),
                )
        sheet_ids_by_name: dict[str, int] = {}
        xml_by_sheet_name: dict[str, str] = {}
        sheet_elements = list(sheets_root) if sheets_root is not None else []
        for sheet_index, sheet in enumerate(sheet_elements, start=1):
            relation_id = sheet.attrib[f'{{{NS_DOCREL}}}id']
            relation = workbook_relations[relation_id]
            xml_path = workbook_target_to_part(relation['Target'])
            sheet_root = ET.fromstring(zf.read(xml_path))
            dimension_node = sheet_root.find(f'{{{NS_MAIN}}}dimension')
            connection.execute(
                '''
                INSERT INTO workbook_sheets (workbook_id, sheet_index, sheet_name, sheet_type, xml_path, dimension_ref)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(workbook_id, sheet_index) DO UPDATE SET
                    sheet_name = excluded.sheet_name,
                    sheet_type = excluded.sheet_type,
                    xml_path = excluded.xml_path,
                    dimension_ref = excluded.dimension_ref
                ''',
                (
                    workbook_id,
                    sheet_index,
                    sheet.attrib['name'],
                    detect_sheet_type(sheet.attrib['name']),
                    xml_path,
                    dimension_node.attrib.get('ref') if dimension_node is not None else None,
                ),
            )
            sheet_id = connection.execute(
                'SELECT id FROM workbook_sheets WHERE workbook_id = ? AND sheet_index = ?',
                (workbook_id, sheet_index),
            ).fetchone()['id']
            sheet_ids_by_name[sheet.attrib['name']] = sheet_id
            xml_by_sheet_name[sheet.attrib['name']] = xml_path
            connection.execute('DELETE FROM assets WHERE sheet_id = ?', (sheet_id,))
            connection.execute('DELETE FROM workbook_sheet_relationships WHERE sheet_id = ?', (sheet_id,))
            connection.execute('DELETE FROM workbook_merged_cells WHERE sheet_id = ?', (sheet_id,))
            connection.execute('DELETE FROM workbook_tables WHERE sheet_id = ?', (sheet_id,))
            connection.execute('DELETE FROM workbook_cells WHERE sheet_id = ?', (sheet_id,))
            rel_path = sheet_relationship_path(xml_path)
            sheet_relations: dict[str, dict[str, str]] = {}
            if rel_path in zf.namelist():
                sheet_relations = parse_relationships(zf.read(rel_path))
                for rel_key, rel_data in sheet_relations.items():
                    connection.execute(
                        '''
                        INSERT INTO workbook_sheet_relationships (sheet_id, rel_id, rel_type, target, target_mode)
                        VALUES (?, ?, ?, ?, ?)
                        ''',
                        (sheet_id, rel_key, rel_data['Type'], rel_data['Target'], rel_data.get('TargetMode') or None),
                    )
            merge_cells = sheet_root.find(f'{{{NS_MAIN}}}mergeCells')
            if merge_cells is not None:
                for merge_cell in merge_cells:
                    connection.execute(
                        'INSERT INTO workbook_merged_cells (sheet_id, merge_ref) VALUES (?, ?)',
                        (sheet_id, merge_cell.attrib['ref']),
                    )
            batch: list[tuple[object, ...]] = []
            for cell in iter_sheet_cells(zf.read(xml_path), shared_strings):
                batch.append(
                    (
                        sheet_id,
                        cell['cell_ref'],
                        cell['row_index'],
                        cell['column_index'],
                        cell['cell_type'],
                        cell['raw_value'],
                        cell['display_value'],
                        cell['formula'],
                        cell['formula_type'],
                    )
                )
                if len(batch) >= 5000:
                    connection.executemany(
                        '''
                        INSERT INTO workbook_cells (
                            sheet_id, cell_ref, row_index, column_index, cell_type,
                            raw_value, display_value, formula, formula_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''',
                        batch,
                    )
                    batch.clear()
            if batch:
                connection.executemany(
                    '''
                    INSERT INTO workbook_cells (
                        sheet_id, cell_ref, row_index, column_index, cell_type,
                        raw_value, display_value, formula, formula_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    batch,
                )
            extract_tables(connection, zf, sheet_id, sheet_relations)
            extract_assets(connection, zf, workbook_id, sheet_id, sheet_relations, extract_dir, sheet.attrib['name'])
    return workbook_id, source_id, sheet_ids_by_name, xml_by_sheet_name, shared_strings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Build a SQLite database from the ComputerCrime workbook.')
    parser.add_argument('--workbook', type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument('--source-dir', type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument('--schema', type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument('--sqlite', type=Path, default=DEFAULT_SQLITE)
    parser.add_argument('--extract-assets-dir', type=Path)
    parser.add_argument('--include-iterations', action='store_true')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.sqlite.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite_connect(args.sqlite)
    try:
        apply_schema(connection, args.schema)
        seed_geographies(connection)
        inventory_source_directory(connection, args.source_dir, args.schema.parent)
        workbook_id, workbook_source_id, sheet_ids_by_name, xml_by_sheet_name, shared_strings = import_workbook_package(
            connection,
            args.workbook,
            args.extract_assets_dir,
        )
        connection.execute('DELETE FROM observations WHERE source_id = ?', (workbook_source_id,))
        connection.execute('DELETE FROM simulation_inputs WHERE source_id = ?', (workbook_source_id,))
        with ZipFile(args.workbook) as zf:
            extract_summary_observations(
                connection,
                zf,
                workbook_source_id,
                sheet_ids_by_name,
                xml_by_sheet_name,
                shared_strings,
            )
            extract_simulations(
                connection,
                zf,
                workbook_source_id,
                sheet_ids_by_name,
                xml_by_sheet_name,
                shared_strings,
                args.include_iterations,
            )
        connection.commit()
        print(f'Workbook imported into {args.sqlite}')
        print(f'Workbook ID: {workbook_id}')
        print('Counts:')
        for table_name in ['sources', 'workbook_sheets', 'workbook_cells', 'assets', 'observations', 'simulation_inputs', 'simulation_outputs']:
            count = connection.execute(f'SELECT COUNT(*) AS count FROM {table_name}').fetchone()['count']
            print(f'  {table_name}: {count}')
    finally:
        connection.close()


if __name__ == '__main__':
    main()
