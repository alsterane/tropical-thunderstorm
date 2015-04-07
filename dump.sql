BEGIN TRANSACTION;
CREATE TABLE experiments (
                     experiment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                     date start_date NOT NULL,
                     description text,
                     goals text,
                     comments text
                     );
CREATE TABLE projects (
                     project_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                     start_date text NOT NULL,
                     title text NOT NULL,
                     description text,
                     goals text,
                     comments text);
CREATE TABLE samples (
                     sample_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                     sample_code text NOT NULL,
                     fabrication_date text NOT NULL,
                     structure text NOT NULL,
                     material text,
                     description text,
                     comments text,
                     path text NOT NULL);
CREATE TABLE spectra (
                     spectra_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                     date text NOT NULL,
                     time text NOT NULL,
                     project_number int NOT NULL,
                     experiment_number int NOT NULL,
                     sample_number int NOT NULL,
                     description text NOT NULL,
                     comments text,
                     acquisition_parameters text,
                     path_to_image text,
                     path_to_spectrum text NOT NULL);
DELETE FROM "sqlite_sequence";
COMMIT;
