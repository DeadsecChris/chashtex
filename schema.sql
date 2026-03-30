PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Sparplaene;
DROP TABLE IF EXISTS Benutzer;
DROP TABLE IF EXISTS ETF_Unternehmen;
DROP TABLE IF EXISTS Unternehmen;
DROP TABLE IF EXISTS ETFs;

-- =========================
-- ETFs
-- =========================
CREATE TABLE ETFs (
    ETFID INTEGER PRIMARY KEY,
    WKN TEXT UNIQUE NOT NULL,
    Bezeichnung TEXT NOT NULL,
    RenditePA REAL
);

-- =========================
-- Unternehmen
-- =========================
CREATE TABLE Unternehmen (
    WKN TEXT PRIMARY KEY,
    Bezeichnung TEXT NOT NULL
);

-- =========================
-- Verbindung ETF ↔ Unternehmen
-- =========================
CREATE TABLE ETF_Unternehmen (
    ETFID INTEGER,
    WKN TEXT,
    PRIMARY KEY (ETFID, WKN),
    FOREIGN KEY (ETFID) REFERENCES ETFs(ETFID),
    FOREIGN KEY (WKN) REFERENCES Unternehmen(WKN)
);

-- =========================
-- Benutzer (NEU)
-- =========================
CREATE TABLE Benutzer (
    BenutzerID INTEGER PRIMARY KEY AUTOINCREMENT,
    Vorname TEXT,
    Nachname TEXT,
    Benutzername TEXT UNIQUE NOT NULL,
    PasswortHash TEXT NOT NULL
);

-- =========================
-- Sparpläne (NEU)
-- =========================
-- =========================
-- Sparpläne (FIXED)
-- =========================
CREATE TABLE Sparplaene (
    SparplanID INTEGER PRIMARY KEY AUTOINCREMENT,
    BenutzerID INTEGER NOT NULL,
    NetSalary REAL NOT NULL,
    Expenses REAL NOT NULL,
    SavingLevel TEXT NOT NULL,
    ETFID INTEGER NOT NULL,
    Years INTEGER NOT NULL,
    InitialInvestment REAL NOT NULL,
    FOREIGN KEY (BenutzerID) REFERENCES Benutzer(BenutzerID),
    FOREIGN KEY (ETFID) REFERENCES ETFs(ETFID)
);

-- =========================
-- ETFs Daten
-- =========================
INSERT INTO ETFs VALUES
(1, 'A0RPWH', 'MSCI World', 8.0),
(2, 'A0YEDG', 'S&P 500', 8.5),
(3, 'A111X9', 'Emerging Markets', 7.2),
(4, '593393', 'iShares Core DAX', 8.4),
(5, 'A2QPVU', 'Defense Tech', 9.0),
(6, 'A2N6LC', 'AI & Big Data', 10.0);

-- =========================
-- Unternehmen Daten
-- =========================
INSERT INTO Unternehmen VALUES

('NVIDA', 'NVIDA'),
('APPLE', 'Apple'),
('MICROSOFT', 'Microsoft'),
('AMAZON', 'Amazon'),
('ALPHABET', 'Alphabet'),

('TSMC', 'Taiwan Semiconductor'),
('TENCENT', 'Tencent'),
('SAMSUNG', 'Samsung Electronics'),
('ALIBABA', 'Alibaba'),
('RELIANCE', 'Reliance Industries'),

('SAP', 'SAP'),
('ALLIANZ', 'Allianz'),
('DTelekom', 'Deutsche Telekom'),
('SIEMENS', 'Siemens'),
('MERCEDES', 'Mercedes-Benz'),

('BOEING', 'Boeing'),
('LOCKHEED', 'Lockheed Martin'),
('RAYTHEON', 'Raytheon'),
('GD', 'General Dynamics'),
('NORTHROP', 'Northrop Grumman'),

('NVIDIA', 'Nvidia'),
('ADOBE', 'Adobe'),
('INTUIT', 'Intuit'),
('NETFLIX', 'Netflix'),
('SALESFORCE', 'Salesforce');

-- =========================
-- ETF ↔ Unternehmen Zuordnung
-- =========================

-- MSCI World
INSERT INTO ETF_Unternehmen VALUES (1,'NVIDA');
INSERT INTO ETF_Unternehmen VALUES (1,'APPLE');
INSERT INTO ETF_Unternehmen VALUES (1,'MICROSOFT');
INSERT INTO ETF_Unternehmen VALUES (1,'AMAZON');
INSERT INTO ETF_Unternehmen VALUES (1,'ALPHABET');

-- S&P 500
INSERT INTO ETF_Unternehmen VALUES (2,'NVIDA');
INSERT INTO ETF_Unternehmen VALUES (2,'APPLE');
INSERT INTO ETF_Unternehmen VALUES (2,'MICROSOFT');
INSERT INTO ETF_Unternehmen VALUES (2,'AMAZON');
INSERT INTO ETF_Unternehmen VALUES (2,'ALPHABET');

-- Emerging Markets
INSERT INTO ETF_Unternehmen VALUES (3, 'TSMC');
INSERT INTO ETF_Unternehmen VALUES (3, 'TENCENT');
INSERT INTO ETF_Unternehmen VALUES (3, 'SAMSUNG');
INSERT INTO ETF_Unternehmen VALUES (3, 'ALIBABA');
INSERT INTO ETF_Unternehmen VALUES (3, 'RELIANCE');

-- DAX
INSERT INTO ETF_Unternehmen VALUES (4, 'SAP');
INSERT INTO ETF_Unternehmen VALUES (4, 'ALLIANZ');
INSERT INTO ETF_Unternehmen VALUES (4, 'DTelekom');
INSERT INTO ETF_Unternehmen VALUES (4, 'SIEMENS');
INSERT INTO ETF_Unternehmen VALUES (4, 'MERCEDES');

-- Defense
INSERT INTO ETF_Unternehmen VALUES (5, 'BOEING');
INSERT INTO ETF_Unternehmen VALUES (5, 'LOCKHEED');
INSERT INTO ETF_Unternehmen VALUES (5, 'RAYTHEON');
INSERT INTO ETF_Unternehmen VALUES (5, 'GD');
INSERT INTO ETF_Unternehmen VALUES (5, 'NORTHROP');

-- AI
INSERT INTO ETF_Unternehmen VALUES (6, 'NVIDIA');
INSERT INTO ETF_Unternehmen VALUES (6, 'ADOBE');
INSERT INTO ETF_Unternehmen VALUES (6, 'INTUIT');
INSERT INTO ETF_Unternehmen VALUES (6, 'NETFLIX');
INSERT INTO ETF_Unternehmen VALUES (6, 'SALESFORCE');