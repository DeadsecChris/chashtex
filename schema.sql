PRAGMA foreign_keys = ON;
 
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
 
CREATE TABLE Unternehmen (
    WKN            TEXT PRIMARY KEY,
    Bezeichnung    TEXT NOT NULL,
    Kurzbeschreibung TEXT
);
 
INSERT INTO Sparfaktor VALUES
(1, 'Gering', 10),
(2, 'Mittel', 20),
(3, 'Hoch', 30),
(4, 'Sehr Hoch', 50);