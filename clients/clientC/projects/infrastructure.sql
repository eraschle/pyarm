-- Tabellendefinitionen

-- Element-Typen
CREATE TABLE IF NOT EXISTS element_types (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- Property Set Definitionen
CREATE TABLE IF NOT EXISTS property_sets (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    element_type_id VARCHAR(50),
    FOREIGN KEY (element_type_id) REFERENCES element_types(id)
);

-- Properties Definitionen
CREATE TABLE IF NOT EXISTS properties (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    unit VARCHAR(20),
    description TEXT,
    property_set_id VARCHAR(50),
    FOREIGN KEY (property_set_id) REFERENCES property_sets(id)
);

-- Element-Typ-Definitionen einfügen
INSERT INTO element_types (id, name, description) VALUES
('FOUNDATION', 'Fundament', 'Beton-Fundament für Masten'),
('MAST', 'Mast', 'Stahlmast für Oberleitungen'),
('YOKE', 'Joch', 'Querträger zwischen Masten'),
('TRACK', 'Gleis', 'Gerades Gleis'),
('CURVED_TRACK', 'Kurvengleis', 'Gleis mit Bogengeometrie'),
('DRAINAGE_PIPE', 'Entwässerungsleitung', 'Rohr zur Entwässerung'),
('DRAINAGE_SHAFT', 'Entwässerungsschacht', 'Schacht zur Entwässerung');

-- Property Set Definitionen einfügen
INSERT INTO property_sets (id, name, description, element_type_id) VALUES
('COMMON_PSET', 'Allgemeine Eigenschaften', 'Gemeinsame Eigenschaften für alle Elemente', NULL),
('GEO_PSET', 'Geometrie', 'Geometrische Eigenschaften', NULL),
('FOUNDATION_PSET', 'Fundamenteigenschaften', 'Spezifische Eigenschaften für Fundamente', 'FOUNDATION'),
('MAST_PSET', 'Masteigenschaften', 'Spezifische Eigenschaften für Masten', 'MAST'),
('TRACK_PSET', 'Gleiseigenschaften', 'Spezifische Eigenschaften für Gleise', 'TRACK'),
('DRAINAGE_PSET', 'Entwässerungseigenschaften', 'Spezifische Eigenschaften für Entwässerungssysteme', NULL);

-- Properties einfügen
INSERT INTO properties (id, name, data_type, unit, description, property_set_id) VALUES
-- Allgemeine Eigenschaften
('PROP_ID', 'ID', 'String', NULL, 'Eindeutige Kennung', 'COMMON_PSET'),
('PROP_NAME', 'Name', 'String', NULL, 'Bezeichnung des Elements', 'COMMON_PSET'),
('PROP_MATERIAL', 'Material', 'String', NULL, 'Material des Elements', 'COMMON_PSET'),
('PROP_DESCRIPTION', 'Beschreibung', 'String', NULL, 'Beschreibung des Elements', 'COMMON_PSET'),
('PROP_CREATION_DATE', 'Erstelldatum', 'Date', NULL, 'Datum der Erstellung', 'COMMON_PSET'),
('PROP_STATUS', 'Status', 'String', NULL, 'Status des Elements', 'COMMON_PSET'),

-- Geometrische Eigenschaften
('PROP_COORD_X', 'X-Koordinate', 'Float', 'm', 'X-Koordinate des Startpunkts', 'GEO_PSET'),
('PROP_COORD_Y', 'Y-Koordinate', 'Float', 'm', 'Y-Koordinate des Startpunkts', 'GEO_PSET'),
('PROP_COORD_Z', 'Z-Koordinate', 'Float', 'm', 'Z-Koordinate des Startpunkts', 'GEO_PSET'),
('PROP_COORD_X2', 'X-Koordinate Ende', 'Float', 'm', 'X-Koordinate des Endpunkts', 'GEO_PSET'),
('PROP_COORD_Y2', 'Y-Koordinate Ende', 'Float', 'm', 'Y-Koordinate des Endpunkts', 'GEO_PSET'),
('PROP_COORD_Z2', 'Z-Koordinate Ende', 'Float', 'm', 'Z-Koordinate des Endpunkts', 'GEO_PSET'),
('PROP_AZIMUTH', 'Azimut', 'Float', 'grad', 'Azimut-Winkel', 'GEO_PSET'),
('PROP_LENGTH', 'Länge', 'Float', 'm', 'Länge des Elements', 'GEO_PSET'),

-- Fundamenteigenschaften
('PROP_FOUNDATION_TYPE', 'Fundamenttyp', 'String', NULL, 'Typ des Fundaments', 'FOUNDATION_PSET'),
('PROP_FOUNDATION_WIDTH', 'Breite', 'Float', 'mm', 'Breite des Fundaments', 'FOUNDATION_PSET'),
('PROP_FOUNDATION_DEPTH', 'Tiefe', 'Float', 'mm', 'Tiefe des Fundaments', 'FOUNDATION_PSET'),
('PROP_FOUNDATION_HEIGHT', 'Höhe', 'Float', 'mm', 'Höhe des Fundaments', 'FOUNDATION_PSET'),
('PROP_CONCRETE_QUALITY', 'Betonqualität', 'String', NULL, 'Qualität des verwendeten Betons', 'FOUNDATION_PSET'),
('PROP_STEEL_QUALITY', 'Stahlqualität', 'String', NULL, 'Qualität des verwendeten Bewehrungsstahls', 'FOUNDATION_PSET'),
('PROP_REINFORCEMENT', 'Bewehrung', 'String', NULL, 'Art der Bewehrung', 'FOUNDATION_PSET'),

-- Masteigenschaften
('PROP_MAST_TYPE', 'Masttyp', 'String', NULL, 'Typ des Masts', 'MAST_PSET'),
('PROP_MAST_HEIGHT', 'Höhe', 'Float', 'mm', 'Höhe des Masts', 'MAST_PSET'),
('PROP_MAST_PROFILE', 'Profiltyp', 'String', NULL, 'Profiltyp des Masts', 'MAST_PSET'),
('PROP_MAST_WEIGHT', 'Gewicht', 'Float', 'kg', 'Gewicht des Masts', 'MAST_PSET'),
('PROP_WIND_LOAD', 'Windlast', 'Float', 'kN/m²', 'Auslegung für Windlast', 'MAST_PSET'),
('PROP_COATING', 'Beschichtung', 'String', NULL, 'Art der Beschichtung', 'MAST_PSET'),

-- Gleiseigenschaften
('PROP_TRACK_GAUGE', 'Spurweite', 'Float', 'mm', 'Spurweite des Gleises', 'TRACK_PSET'),
('PROP_TRACK_TYPE', 'Gleistyp', 'String', NULL, 'Typ des Gleises', 'TRACK_PSET'),
('PROP_TRACK_CANT', 'Überhöhung', 'Float', 'mm', 'Überhöhung des Gleises', 'TRACK_PSET'),
('PROP_RAIL_PROFILE', 'Schienenprofil', 'String', NULL, 'Profil der Schienen', 'TRACK_PSET'),
('PROP_SLEEPER_TYPE', 'Schwellentyp', 'String', NULL, 'Typ der Schwellen', 'TRACK_PSET'),
('PROP_BALLAST_TYPE', 'Schottertyp', 'String', NULL, 'Typ des Schotters', 'TRACK_PSET'),
('PROP_CLOTHOID_PARAM', 'Klothoidenparameter', 'Float', NULL, 'Parameter der Klothoide', 'TRACK_PSET'),
('PROP_START_RADIUS', 'Startradius', 'Float', 'm', 'Radius am Anfang der Kurve', 'TRACK_PSET'),
('PROP_END_RADIUS', 'Endradius', 'Float', 'm', 'Radius am Ende der Kurve', 'TRACK_PSET'),

-- Entwässerungseigenschaften
('PROP_DRAINAGE_TYPE', 'Entwässerungstyp', 'String', NULL, 'Typ des Entwässerungselements', 'DRAINAGE_PSET'),
('PROP_DRAINAGE_DIAMETER', 'Durchmesser', 'Float', 'mm', 'Durchmesser des Entwässerungselements', 'DRAINAGE_PSET'),
('PROP_DRAINAGE_SLOPE', 'Gefälle', 'Float', '‰', 'Gefälle der Entwässerungsleitung', 'DRAINAGE_PSET'),
('PROP_DRAINAGE_CAPACITY', 'Kapazität', 'Float', 'l/s', 'Durchflusskapazität', 'DRAINAGE_PSET'),
('PROP_PIPE_QUALITY', 'Rohrqualität', 'String', NULL, 'Qualitätsklasse des Rohrs', 'DRAINAGE_PSET'),
('PROP_CONNECTION_TYPE', 'Verbindungstyp', 'String', NULL, 'Art der Rohrverbindung', 'DRAINAGE_PSET');

-- Element-Property-Verknüpfungen
CREATE TABLE IF NOT EXISTS element_properties (
    element_id VARCHAR(50),
    property_id VARCHAR(50),
    value_string TEXT,
    value_number FLOAT,
    value_boolean BOOLEAN,
    value_date DATE,
    PRIMARY KEY (element_id, property_id),
    FOREIGN KEY (property_id) REFERENCES properties(id)
);

-- Haupttabellen für die verschiedenen Elementtypen

-- Fundamente
CREATE TABLE IF NOT EXISTS foundations (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    coord_x FLOAT,
    coord_y FLOAT,
    coord_z FLOAT,
    type VARCHAR(50),
    width_mm FLOAT,
    depth_mm FLOAT,
    height_mm FLOAT,
    material VARCHAR(50),
    creation_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'active'
);

-- Masten
CREATE TABLE IF NOT EXISTS masts (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    coord_x FLOAT,
    coord_y FLOAT,
    coord_z FLOAT,
    type VARCHAR(50),
    height_mm FLOAT,
    azimuth FLOAT,
    material VARCHAR(50),
    profile VARCHAR(50),
    foundation_id VARCHAR(50),
    weight_kg FLOAT,
    wind_load FLOAT,
    coating VARCHAR(50),
    creation_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'active',
    FOREIGN KEY (foundation_id) REFERENCES foundations(id)
);

-- Joche
CREATE TABLE IF NOT EXISTS yokes (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    coord_x1 FLOAT,
    coord_y1 FLOAT,
    coord_z1 FLOAT,
    coord_x2 FLOAT,
    coord_y2 FLOAT,
    coord_z2 FLOAT,
    type VARCHAR(50),
    span_mm FLOAT,
    material VARCHAR(50),
    mast_id1 VARCHAR(50),
    mast_id2 VARCHAR(50),
    creation_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'active',
    FOREIGN KEY (mast_id1) REFERENCES masts(id),
    FOREIGN KEY (mast_id2) REFERENCES masts(id)
);

-- Schienen
CREATE TABLE IF NOT EXISTS tracks (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    coord_x1 FLOAT,
    coord_y1 FLOAT,
    coord_z1 FLOAT,
    coord_x2 FLOAT,
    coord_y2 FLOAT,
    coord_z2 FLOAT,
    gauge_mm FLOAT,
    type VARCHAR(50),
    cant_mm FLOAT,
    rail_profile VARCHAR(50),
    sleeper_type VARCHAR(50),
    ballast_type VARCHAR(50),
    creation_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'active'
);

-- Kurvenschienen
CREATE TABLE IF NOT EXISTS curved_tracks (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    coord_x1 FLOAT,
    coord_y1 FLOAT,
    coord_z1 FLOAT,
    coord_x2 FLOAT,
    coord_y2 FLOAT,
    coord_z2 FLOAT,
    gauge_mm FLOAT,
    type VARCHAR(50),
    cant_mm FLOAT,
    clothoid_param FLOAT,
    start_radius_m FLOAT,
    end_radius_m FLOAT,
    rail_profile VARCHAR(50),
    sleeper_type VARCHAR(50),
    ballast_type VARCHAR(50),
    creation_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'active'
);

-- Entwässerung
CREATE TABLE IF NOT EXISTS drainage (
    id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    coord_x1 FLOAT,
    coord_y1 FLOAT,
    coord_z1 FLOAT,
    coord_x2 FLOAT,
    coord_y2 FLOAT,
    coord_z2 FLOAT,
    diameter_mm FLOAT,
    material VARCHAR(50),
    slope_permille FLOAT,
    capacity FLOAT,
    pipe_quality VARCHAR(50),
    connection_type VARCHAR(50),
    creation_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'active'
);

-- Daten für Fundamente
INSERT INTO foundations (id, name, coord_x, coord_y, coord_z, type, width_mm, depth_mm, height_mm, material, creation_date, status) VALUES
('F001', 'Fundament 1', 2600000.0, 1200000.0, 456.78, 'Typ A', 1500, 2000, 1000, 'Beton', '2023-05-15', 'active'),
('F002', 'Fundament 2', 2600050.0, 1200010.0, 457.12, 'Typ B', 1800, 2200, 1200, 'Beton', '2023-05-15', 'active'),
('F003', 'Fundament 3', 2600100.0, 1200020.0, 457.45, 'Typ A', 1500, 2000, 1000, 'Beton', '2023-05-15', 'active'),
('F004', 'Fundament 4', 2600150.0, 1200030.0, 457.80, 'Typ C', 2000, 2500, 1300, 'Stahlbeton', '2023-05-16', 'active'),
('F005', 'Fundament 5', 2600200.0, 1200040.0, 458.10, 'Typ B', 1800, 2200, 1200, 'Beton', '2023-05-16', 'active');

-- Daten für Masten
INSERT INTO masts (id, name, coord_x, coord_y, coord_z, type, height_mm, azimuth, material, profile, foundation_id, weight_kg, wind_load, coating, creation_date, status) VALUES
('M001', 'Mast 1', 2600000.0, 1200000.0, 456.78, 'DP20', 8500, 45.0, 'Stahl', 'HEB', 'F001', 780.5, 0.8, 'Verzinkt', '2023-05-20', 'active'),
('M002', 'Mast 2', 2600050.0, 1200010.0, 457.12, 'DP22', 9000, 45.0, 'Stahl', 'HEB', 'F002', 820.0, 0.9, 'Verzinkt', '2023-05-20', 'active'),
('M003', 'Mast 3', 2600100.0, 1200020.0, 457.45, 'DP20', 8500, 45.0, 'Stahl', 'HEB', 'F003', 780.5, 0.8, 'Verzinkt', '2023-05-20', 'active'),
('M004', 'Mast 4', 2600150.0, 1200030.0, 457.80, 'DP25', 10000, 45.0, 'Stahl', 'HEA', 'F004', 950.0, 1.0, 'Pulverbeschichtet', '2023-05-21', 'active'),
('M005', 'Mast 5', 2600200.0, 1200040.0, 458.10, 'DP22', 9000, 45.0, 'Stahl', 'HEB', 'F005', 820.0, 0.9, 'Verzinkt', '2023-05-21', 'active');

-- Daten für Joche
INSERT INTO yokes (id, name, coord_x1, coord_y1, coord_z1, coord_x2, coord_y2, coord_z2, type, span_mm, material, mast_id1, mast_id2, creation_date, status) VALUES
('J001', 'Joch 1-2', 2600000.0, 1200000.0, 465.28, 2600050.0, 1200010.0, 465.62, 'RI', 50990, 'Stahl', 'M001', 'M002', '2023-05-25', 'active'),
('J002', 'Joch 2-3', 2600050.0, 1200010.0, 465.62, 2600100.0, 1200020.0, 465.95, 'RII', 53850, 'Stahl', 'M002', 'M003', '2023-05-25', 'active'),
('J003', 'Joch 3-4', 2600100.0, 1200020.0, 465.95, 2600150.0, 1200030.0, 466.30, 'RI', 52100, 'Stahl', 'M003', 'M004', '2023-05-26', 'active'),
('J004', 'Joch 4-5', 2600150.0, 1200030.0, 466.30, 2600200.0, 1200040.0, 466.60, 'RIII', 51750, 'Aluminium', 'M004', 'M005', '2023-05-26', 'active');

-- Daten für Schienen
INSERT INTO tracks (id, name, coord_x1, coord_y1, coord_z1, coord_x2, coord_y2, coord_z2, gauge_mm, type, cant_mm, rail_profile, sleeper_type, ballast_type, creation_date, status) VALUES
('T001', 'Gleis 1', 2600010.0, 1200030.0, 456.78, 2600110.0, 1200050.0, 457.45, 1435, 'UIC60', 50, 'UIC60', 'B70', 'Basalt', '2023-05-28', 'active'),
('T002', 'Gleis 2', 2600010.0, 1200035.0, 456.78, 2600110.0, 1200055.0, 457.45, 1435, 'UIC60', 50, 'UIC60', 'B70', 'Basalt', '2023-05-28', 'active'),
('T003', 'Gleis 3', 2600010.0, 1200040.0, 456.78, 2600110.0, 1200060.0, 457.45, 1435, 'UIC54', 40, 'UIC54', 'B70', 'Basalt', '2023-05-29', 'active'),
('T004', 'Gleis 4', 2600010.0, 1200045.0, 456.78, 2600110.0, 1200065.0, 457.45, 1000, 'S49', 30, 'S49', 'Holz', 'Granit', '2023-05-29', 'active');

-- Daten für Kurvenschienen
INSERT INTO curved_tracks (id, name, coord_x1, coord_y1, coord_z1, coord_x2, coord_y2, coord_z2, gauge_mm, type, cant_mm, clothoid_param, start_radius_m, end_radius_m, rail_profile, sleeper_type, ballast_type, creation_date, status) VALUES
('CT001', 'Kurvengleis 1', 2600110.0, 1200050.0, 457.45, 2600210.0, 1200150.0, 458.12, 1435, 'UIC60', 120, 150.0, NULL, 500.0, 'UIC60', 'B70', 'Basalt', '2023-06-01', 'active'),
('CT002', 'Kurvengleis 2', 2600110.0, 1200055.0, 457.45, 2600210.0, 1200155.0, 458.12, 1435, 'UIC60', 120, 150.0, NULL, 500.0, 'UIC60', 'B70', 'Basalt', '2023-06-01', 'active'),
('CT003', 'Kurvengleis 3', 2600110.0, 1200060.0, 457.45, 2600210.0, 1200160.0, 458.12, 1435, 'UIC54', 130, 130.0, NULL, 450.0, 'UIC54', 'B70', 'Basalt', '2023-06-02', 'active'),
('CT004', 'Kurvengleis 4', 2600110.0, 1200065.0, 457.45, 2600210.0, 1200165.0, 458.12, 1000, 'S49', 90, 100.0, NULL, 300.0, 'S49', 'Holz', 'Granit', '2023-06-02', 'active');

-- Daten für Entwässerung
INSERT INTO drainage (id, type, name, coord_x1, coord_y1, coord_z1, coord_x2, coord_y2, coord_z2, diameter_mm, material, slope_permille, capacity, pipe_quality, connection_type, creation_date, status) VALUES
('D001', 'Pipe', 'Entwässerungsleitung 1', 2600015.0, 1200025.0, 456.28, 2600115.0, 1200045.0, 455.78, 300, 'PVC', 10, 15.5, 'SN8', 'Steckmuffe', '2023-06-05', 'active'),
('D002', 'Shaft', 'Entwässerungsschacht 1', 2600015.0, 1200025.0, 456.28, NULL, NULL, NULL, 800, 'Beton', NULL, NULL, NULL, NULL, '2023-06-05', 'active'),
('D003', 'Shaft', 'Entwässerungsschacht 2', 2600115.0, 1200045.0, 455.78, NULL, NULL, NULL, 800, 'Beton', NULL, NULL, NULL, NULL, '2023-06-05', 'active'),
('D004', 'Pipe', 'Entwässerungsleitung 2', 2600115.0, 1200045.0, 455.78, 2600215.0, 1200065.0, 455.28, 400, 'PVC', 5, 25.0, 'SN12', 'Steckmuffe', '2023-06-06', 'active'),
('D005', 'Shaft', 'Entwässerungsschacht 3', 2600215.0, 1200065.0, 455.28, NULL, NULL, NULL, 1000, 'Beton', NULL, NULL, NULL, NULL, '2023-06-06', 'active');

-- Verknüpfungen zwischen Elementen und Properties einfügen (Beispiele)

-- Fundament 1 Properties
INSERT INTO element_properties (element_id, property_id, value_string, value_number, value_boolean, value_date) VALUES
('F001', 'PROP_ID', 'F001', NULL, NULL, NULL),
('F001', 'PROP_NAME', 'Fundament 1', NULL, NULL, NULL),
('F001', 'PROP_MATERIAL', 'Beton', NULL, NULL, NULL),
('F001', 'PROP_DESCRIPTION', 'Standardfundament für DP20-Mast', NULL, NULL, NULL),
('F001', 'PROP_CREATION_DATE', NULL, NULL, NULL, '2023-05-15'),
('F001', 'PROP_STATUS', 'active', NULL, NULL, NULL),
('F001', 'PROP_COORD_X', NULL, 2600000.0, NULL, NULL),
('F001', 'PROP_COORD_Y', NULL, 1200000.0, NULL, NULL),
('F001', 'PROP_COORD_Z', NULL, 456.78, NULL, NULL),
('F001', 'PROP_FOUNDATION_TYPE', 'Typ A', NULL, NULL, NULL),
('F001', 'PROP_FOUNDATION_WIDTH', NULL, 1500.0, NULL, NULL),
('F001', 'PROP_FOUNDATION_DEPTH', NULL, 2000.0, NULL, NULL),
('F001', 'PROP_FOUNDATION_HEIGHT', NULL, 1000.0, NULL, NULL),
('F001', 'PROP_CONCRETE_QUALITY', 'C30/37', NULL, NULL, NULL),
('F001', 'PROP_STEEL_QUALITY', 'B500B', NULL, NULL, NULL),
('F001', 'PROP_REINFORCEMENT', 'Bewehrungsmatte Q257', NULL, NULL, NULL);

-- Mast 1 Properties
INSERT INTO element_properties (element_id, property_id, value_string, value_number, value_boolean, value_date) VALUES
('M001', 'PROP_ID', 'M001', NULL, NULL, NULL),
('M001', 'PROP_NAME', 'Mast 1', NULL, NULL, NULL),
('M001', 'PROP_MATERIAL', 'Stahl', NULL, NULL, NULL),
('M001', 'PROP_DESCRIPTION', 'Standardmast DP20', NULL, NULL, NULL),
('M001', 'PROP_CREATION_DATE', NULL, NULL, NULL, '2023-05-20'),
('M001', 'PROP_STATUS', 'active', NULL, NULL, NULL),
('M001', 'PROP_COORD_X', NULL, 2600000.0, NULL, NULL),
('M001', 'PROP_COORD_Y', NULL, 1200000.0, NULL, NULL),
('M001', 'PROP_COORD_Z', NULL, 456.78, NULL, NULL),
('M001', 'PROP_AZIMUTH', NULL, 45.0, NULL, NULL),
('M001', 'PROP_MAST_TYPE', 'DP20', NULL, NULL, NULL),
('M001', 'PROP_MAST_HEIGHT', NULL, 8500.0, NULL, NULL),
('M001', 'PROP_MAST_PROFILE', 'HEB', NULL, NULL, NULL),
('M001', 'PROP_MAST_WEIGHT', NULL, 780.5, NULL, NULL),
('M001', 'PROP_WIND_LOAD', NULL, 0.8, NULL, NULL),
('M001', 'PROP_COATING', 'Verzinkt', NULL, NULL, NULL);

-- Track 1 Properties
INSERT INTO element_properties (element_id, property_id, value_string, value_number, value_boolean, value_date) VALUES
('T001', 'PROP_ID', 'T001', NULL, NULL, NULL),
('T001', 'PROP_NAME', 'Gleis 1', NULL, NULL, NULL),
('T001', 'PROP_DESCRIPTION', 'Hauptgleis UIC60', NULL, NULL, NULL),
('T001', 'PROP_CREATION_DATE', NULL, NULL, NULL, '2023-05-28'),
('T001', 'PROP_STATUS', 'active', NULL, NULL, NULL),
('T001', 'PROP_COORD_X', NULL, 2600010.0, NULL, NULL),
('T001', 'PROP_COORD_Y', NULL, 1200030.0, NULL, NULL),
('T001', 'PROP_COORD_Z', NULL, 456.78, NULL, NULL),
('T001', 'PROP_COORD_X2', NULL, 2600110.0, NULL, NULL),
('T001', 'PROP_COORD_Y2', NULL, 1200050.0, NULL, NULL),
('T001', 'PROP_COORD_Z2', NULL, 457.45, NULL, NULL),
('T001', 'PROP_LENGTH', NULL, 103.08, NULL, NULL),
('T001', 'PROP_TRACK_GAUGE', NULL, 1435.0, NULL, NULL),
('T001', 'PROP_TRACK_TYPE', 'UIC60', NULL, NULL, NULL),
('T001', 'PROP_TRACK_CANT', NULL, 50.0, NULL, NULL),
('T001', 'PROP_RAIL_PROFILE', 'UIC60', NULL, NULL, NULL),
('T001', 'PROP_SLEEPER_TYPE', 'B70', NULL, NULL, NULL),
('T001', 'PROP_BALLAST_TYPE', 'Basalt', NULL, NULL, NULL);

-- Drainage Properties
INSERT INTO element_properties (element_id, property_id, value_string, value_number, value_boolean, value_date) VALUES
('D001', 'PROP_ID', 'D001', NULL, NULL, NULL),
('D001', 'PROP_NAME', 'Entwässerungsleitung 1', NULL, NULL, NULL),
('D001', 'PROP_MATERIAL', 'PVC', NULL, NULL, NULL),
('D001', 'PROP_DESCRIPTION', 'Hauptentwässerungsleitung', NULL, NULL, NULL),
('D001', 'PROP_CREATION_DATE', NULL, NULL, NULL, '2023-06-05'),
('D001', 'PROP_STATUS', 'active', NULL, NULL, NULL),
('D001', 'PROP_COORD_X', NULL, 2600015.0, NULL, NULL),
('D001', 'PROP_COORD_Y', NULL, 1200025.0, NULL, NULL),
('D001', 'PROP_COORD_Z', NULL, 456.28, NULL, NULL),
('D001', 'PROP_COORD_X2', NULL, 2600115.0, NULL, NULL),
('D001', 'PROP_COORD_Y2', NULL, 1200045.0, NULL, NULL),
('D001', 'PROP_COORD_Z2', NULL, 455.78, NULL, NULL),
('D001', 'PROP_LENGTH', NULL, 102.47, NULL, NULL),
('D001', 'PROP_DRAINAGE_TYPE', 'Pipe', NULL, NULL, NULL),
('D001', 'PROP_DRAINAGE_DIAMETER', NULL, 300.0, NULL, NULL),
('D001', 'PROP_DRAINAGE_SLOPE', NULL, 10.0, NULL, NULL),
('D001', 'PROP_DRAINAGE_CAPACITY', NULL, 15.5, NULL, NULL),
('D001', 'PROP_PIPE_QUALITY', 'SN8', NULL, NULL, NULL),
('D001', 'PROP_CONNECTION_TYPE', 'Steckmuffe', NULL, NULL, NULL);