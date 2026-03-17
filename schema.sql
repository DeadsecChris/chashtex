PRAGMA foreign_keys = ON;

-- =========================
-- Tabellen
-- =========================

CREATE TABLE Sparfaktor (
    SparfaktorID INTEGER PRIMARY KEY,
    Bezeichnung  TEXT UNIQUE NOT NULL,
    Prozent      REAL NOT NULL
);

CREATE TABLE Sparrate (
    SparrateID   INTEGER PRIMARY KEY,
    Ergebnis     REAL,
    NettoEinkomm REAL,
    Ausgaben     REAL,
    SparfaktorID INTEGER NOT NULL,
    FOREIGN KEY (SparfaktorID) REFERENCES Sparfaktor(SparfaktorID)
);

CREATE TABLE ETFs (
    ETFID        INTEGER PRIMARY KEY,
    WKN          TEXT UNIQUE NOT NULL,
    Bezeichnung  TEXT NOT NULL,
    RenditePA    REAL
);

CREATE TABLE Sparplan (
    SparplanID INTEGER PRIMARY KEY,
    Beschreibung TEXT,
    SparrateID INTEGER,
    ETFID INTEGER,
    FOREIGN KEY (SparrateID) REFERENCES Sparrate(SparrateID),
    FOREIGN KEY (ETFID) REFERENCES ETFs(ETFID)
);

CREATE TABLE Personen (
    PersID          INTEGER PRIMARY KEY,
    Vorname         TEXT NOT NULL,
    Nachname        TEXT NOT NULL,
    Geburtsdatum    TEXT NOT NULL,
    Anlagevermoegen REAL,
    Bankguthaben    REAL,
    SparrateID      INTEGER,
    SparplanID      INTEGER,
    FOREIGN KEY (SparrateID) REFERENCES Sparrate(SparrateID),
    FOREIGN KEY (SparplanID) REFERENCES Sparplan(SparplanID)
);

-- Unternehmen
CREATE TABLE Unternehmen (
    WKN TEXT PRIMARY KEY,
    Bezeichnung TEXT NOT NULL,
    Kurzbeschreibung TEXT
);

-- NEU: Verknüpfung ETF ↔ Unternehmen
CREATE TABLE ETF_Unternehmen (
    ETFID INTEGER,
    WKN TEXT,
    PRIMARY KEY (ETFID, WKN),
    FOREIGN KEY (ETFID) REFERENCES ETFs(ETFID),
    FOREIGN KEY (WKN) REFERENCES Unternehmen(WKN)
);

-- =========================
-- Stammdaten
-- =========================

INSERT INTO Sparfaktor VALUES
(1, 'Gering', 10),
(2, 'Mittel', 20),
(3, 'Hoch', 30),
(4, 'Sehr Hoch', 50);

INSERT INTO ETFs VALUES
(1, 'A0RPWH', 'MSCI World', 8.0),
(2, 'A0YEDG', 'S&P 500', 8.5),
(3, 'A111X9', 'Emerging Markets', 7.2);


-- =========================
-- Unternehmen (Beispiele)
-- =========================

INSERT INTO Unternehmen VALUES
('US0378331005', 'Apple', 'Technologieunternehmen'),
('US5949181045', 'Microsoft', 'Software und Cloud'),
('US02079K3059', 'Alphabet (Google)', 'Internet & Werbung'),
('US30303M1027', 'Meta Platforms', 'Social Media'),
('US0231351067', 'Amazon', 'E-Commerce & Cloud'),
('US88160R1014', 'Tesla', 'Elektroautos'),
('US4592001014', 'IBM', 'IT & Beratung'),
('US7427181091', 'Procter & Gamble', 'Konsumgüter'),
('US46625H1005', 'JPMorgan Chase', 'Bank'),
('US0846707026', 'Berkshire Hathaway', 'Investmentholding');

-- =========================
-- ETF → Unternehmen Zuordnung
-- =========================

-- MSCI World
INSERT INTO ETF_Unternehmen VALUES (1, 'US0378331005'); -- Apple
INSERT INTO ETF_Unternehmen VALUES (1, 'US5949181045'); -- Microsoft
INSERT INTO ETF_Unternehmen VALUES (1, 'US02079K3059'); -- Alphabet
INSERT INTO ETF_Unternehmen VALUES (1, 'US30303M1027'); -- Meta
INSERT INTO ETF_Unternehmen VALUES (1, 'US0231351067'); -- Amazon

-- S&P 500
INSERT INTO ETF_Unternehmen VALUES (2, 'US0378331005'); -- Apple
INSERT INTO ETF_Unternehmen VALUES (2, 'US5949181045'); -- Microsoft
INSERT INTO ETF_Unternehmen VALUES (2, 'US88160R1014'); -- Tesla
INSERT INTO ETF_Unternehmen VALUES (2, 'US0231351067'); -- Amazon
INSERT INTO ETF_Unternehmen VALUES (2, 'US02079K3059'); -- Alphabet

-- Emerging Markets (Beispielhaft gemischt)
INSERT INTO ETF_Unternehmen VALUES (3, 'US30303M1027'); -- Meta
INSERT INTO ETF_Unternehmen VALUES (3, 'US4592001014'); -- IBM
INSERT INTO ETF_Unternehmen VALUES (3, 'US7427181091'); -- P&G
INSERT INTO ETF_Unternehmen VALUES (3, 'US46625H1005'); -- JPMorgan
INSERT INTO ETF_Unternehmen VALUES (3, 'US0846707026'); -- Berkshire

