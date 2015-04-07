__author__ = 'loh20'


import sqlite3
import uuid
import SharedDefinitions as shrd
import time


class DatabaseControl:
    """
    Contains functions used to control the setup and structure of the database.
    """

    def __init__(self):
        """
        Initialises the database controller.
        :return:
        """

    @staticmethod
    def create(base_path):
        """
        Creates database in path which keeps list of file paths. In principle, this function only serves to create a
        database once.
        :param base_path: String denoting path.
        """
        db_path = base_path + '\Database_' + str(uuid.uuid4()) + '.db'
        db = sqlite3.connect(str(db_path))

        shrd.__DB_PATH__ = str(db_path)
        cursor = db.cursor()
        # PROJECTS TABLE
        cursor.execute('''
            CREATE TABLE projects(project_id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT,
                       title TEXT, description TEXT, goals TEXT, comments TEXT)
        ''')

        # SAMPLE TABLE
        cursor.execute('''CREATE TABLE samples (
                     sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     sample_code text NOT NULL,
                     fabrication_date text NOT NULL,
                     structure text NOT NULL,
                     material text,
                     description text,
                     comments text,
                     path text NOT NULL)''')

        # EXPERIMENT TABLE
        cursor.execute('''CREATE TABLE experiments (
                     experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date text NOT NULL,
                     title text,
                     description text,
                     goals text,
                     comments text
                     )''')

        # SPECTRA TABLE
        cursor.execute('''CREATE TABLE spectra (
                     spectra_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date text NOT NULL,
                     time text NOT NULL,
                     project_number int NOT NULL,
                     experiment_number int NOT NULL,
                     sample_number int NOT NULL,
                     description text NOT NULL,
                     comments text,
                     acquisition_parameters text,
                     path_to_image text,
                     path_to_spectrum text NOT NULL)''')

        db.commit()
        db.close()

    @staticmethod
    def add_project(title, description, goals, comments):
        """
        Adds a new project to database.
        :return:
        """
        creation_year = time.strftime("%Y")
        creation_month = time.strftime("%m")
        creation_day = time.strftime("%d")
        date = creation_year + '-' + creation_month + '-' + creation_day
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        try:
            cursor.execute('''INSERT INTO projects(date, title, description, goals, comments)  VALUES(?,?,?,?,?)''',
                           (str(date), str(title), str(description), str(goals), str(comments)))
            print("New project added to database.")
        except sqlite3.IntegrityError:
            print('Record already exists.')
        db.commit()
        db.close()

    def add_sample(self, sample_code, fabrication_date, structure, material, description, comments, path_to_supp):
        """
        Adds a new sample to database.
        :return:
        """
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        try:
            cursor.execute('''INSERT INTO samples(sample_code, fabrication_date, structure, material,
            description, comments, path)  VALUES(?,?,?,?,?,?,?)''',
                           (str(sample_code), str(fabrication_date), str(structure), str(material), str(description),
                            str(comments), str(path_to_supp)))
            print("New sample inserted into database.")
        except sqlite3.IntegrityError:
            print('Record already exists.')
        db.commit()
        db.close()

    def add_experiment(self, title, description, goals, comments):
        """
        Adds a new experiment to database.
        :return:
        """
        creation_year = time.strftime("%Y")
        creation_month = time.strftime("%m")
        creation_day = time.strftime("%d")
        date = creation_year + '-' + creation_month + '-' + creation_day
        db = sqlite3.connect(shrd.__DB_PATH__)
        print shrd.__DB_PATH__
        cursor = db.cursor()
        try:
            cursor.execute('''INSERT INTO experiments(date, title, description, goals, comments)  VALUES(?,?,?,?,?)''',
                           (str(date), str(title), str(description), str(goals), str(comments)))
            db.commit()
            db.close()
            print("Experiment added to database.")
        except sqlite3.IntegrityError:
            print('Record already exists.')
            db.close()

    def get_project(self, search_string):
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cmd = '''SELECT * from projects WHERE(date || title || description || goals || comments)
                LIKE '%''' + str(search_string) + '''%' '''
        results = cursor.execute(cmd)
        return_value = results.fetchall()
        print return_value
        db.commit()
        db.close()
        return return_value

    def get_sample(self, search_string):
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cmd = '''SELECT * from samples WHERE(sample_code || fabrication_date || structure
                || material || description || comments)
                LIKE '%''' + str(search_string) + '''%' '''
        results = cursor.execute(cmd)
        return_value = results.fetchall()
        db.commit()
        db.close()
        return return_value

    def get_experiment(self, search_string):
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cmd = '''SELECT * from experiments WHERE(date || title
                || description || goals || comments)
                LIKE '%''' + str(search_string) + '''%' '''
        results = cursor.execute(cmd)
        return_value = results.fetchall()
        db.commit()
        db.close()
        return return_value

    def get_spectrum(self, search_string):
        """
        Returns all experiments which match the search string.
        :param search_string: search string.
        :return:
        """
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cmd = '''SELECT * from spectra WHERE(date || time || description || comments || acquisition_parameters)
                LIKE '%''' + str(search_string) + '''%' AND description LIKE '%Spectrum:%' '''
        results = cursor.execute(cmd)
        return_value = results.fetchall()
        db.commit()
        db.close()
        return return_value

    def get_kinetic_scan(self, search_string):
        """
        Returns all experiments which match the search string.
        :param search_string: search string.
        :return:
        """
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cmd = '''SELECT * from spectra WHERE(date || time || description || comments || acquisition_parameters)
                LIKE '%''' + str(search_string) + '''%' AND description LIKE '%Kinetic Scan:%' '''
        results = cursor.execute(cmd)
        return_value = results.fetchall()
        db.commit()
        db.close()
        return return_value

    def get_raster_scan(self, search_string):
        """
        Returns all experiments which match the search string.
        :param search_string: search string.
        :return:
        """
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cmd = '''SELECT * from spectra WHERE(date || time || description || comments || acquisition_parameters)
                LIKE '%''' + str(search_string) + '''%' AND description LIKE '%Raster Scan:%' '''
        results = cursor.execute(cmd)
        return_value = results.fetchall()
        db.commit()
        db.close()
        return return_value



    def get_last_project_id(self):
        """
        Returns the last project id in the projects table.
        :return: int Last project id.
        """
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cursor.execute('SELECT max(project_id) FROM projects')
        max_id = cursor.fetchone()[0]
        db.commit()
        db.close()
        return max_id

    def get_last_sample_id(self):
        """
        Returns the last sample id in the samples table.
        :return: int Last sample id.
        """
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cursor.execute('SELECT max(sample_id) FROM samples')
        max_id = cursor.fetchone()[0]
        db.commit()
        db.close()
        return max_id

    def get_last_experiment_id(self):
        """
        Returns the last experiment id in the experiments table.
        :return: int Last experiment id.
        """
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cursor.execute('SELECT max(experiment_id) FROM experiments')
        max_id = cursor.fetchone()[0]
        db.commit()
        db.close()
        return max_id

    def get_last_spectra_id(self):
        """
        Returns the last spectra id in the spectra table.
        :return: int Last spectra id.
        """
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cursor.execute('''SELECT max(spectra_id) FROM spectra WHERE description LIKE '%Spectrum:%' ''')
        max_id = cursor.fetchone()[0]
        db.commit()
        db.close()
        return max_id

    def get_last_n_spectra(self, n):
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        cmd = '''SELECT * from spectra WHERE description LIKE '%Spectrum:%' order by spectra_id limit ''' \
              + str(n) + ''
        results = cursor.execute(cmd)
        return_value = results.fetchall()
        db.commit()
        db.close()
        return return_value




