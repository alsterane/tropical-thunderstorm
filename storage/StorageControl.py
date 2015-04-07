__author__ = 'df-setup-basement'

import sqlite3
import time
import numpy as np
import os
import uuid     # generate unique identifiers
import SharedDefinitions as shrd


class StorageControl:

    def __init__(self):
        print("Storage control initialised successfully.")


    def auto_store_kinetic_scan(self, path, time_series_data):
        """
        Automatically saves a kinetic scan to a .txt file and adds an entry to the database.
        Format of kinetic scan data:
                2D numpy array with first entry at [0][0] = 0, then column below wavelengths and then counts 1, counts 2
                and first row after first entry is timing wave
                0       timing[0]       timing[1]       .....         timing[m]
                wl[0]   countsA[0]      countsB[0]
                wl[1]
                ...
                wl[n]
        :param time_series_data:
        :param time_series_params:
        """
        # Write the array to disk
        path = shrd.__DATA_ROOT__ + path
        with file(path, 'w') as outfile:
            # Any line starting with "#" will be ignored by numpy.loadtxt
            outfile.write('# Array shape: {0}\n'.format(time_series_data.shape))
            np.savetxt(outfile, time_series_data, fmt='%7.9f', delimiter='\t')


    def auto_store_image(self, image_data, image_description):
        """
        Automatically stores image as a .jpg file in predefined structure and adds an entry to the database.
        :param image_data:
        :param image_description:
        :return:
        """

        print("This is a stub.")

    def auto_store_raster_scan(self, path, raster_scan_data, position_params):
        """
        Stores raster scan data in the format:
        #(dimx, dimy)
        #(pointsx, pointsy)
        # points along columns
        wl1 spec1   spec2   spec3 .....         specn
        wl2 spec1   spec2   spec3   ....
        .
        .
        :param base_path:
        :param raster_scan_data:
        :return:
        """
        # Write the array to disk
        path = shrd.__DATA_ROOT__ + path
        print path
        with file(path, 'w') as outfile:
            # Any line starting with "#" will be ignored by numpy.loadtxt
            outfile.write('# Array shape: {0}\n'.format(raster_scan_data.shape))
            outfile.write('#[nx, ny, x_dist, y_dist, x_0, y_0]\n')
            outfile.write(str(position_params) + '\n')
            np.savetxt(outfile, raster_scan_data, fmt='%7.9f', delimiter='\t')

    def auto_store_spectrum(self, path, spectrum_data, spectrum_params):
        """
        Automatically stores spectral data as two column .txt file in appropriate path structure.
        :param base_path: Base path of data origin folder.
        :param spectrum_data: Numpy array, 2D, with [wavelength, counts]. Spectral data to be saved. Can also be
        [wavelength, counts, bg] or [wavelength, counts, bg, ref]
        :param spectrum_params: Holds paramters associated with spectrum.
        """
        # Write the array to disk
        path = shrd.__DATA_ROOT__ + path
        with file(path, 'w') as outfile:
            # Any line starting with "#" will be ignored by numpy.loadtxt
            outfile.write('# Array shape: {0}\n'.format(spectrum_data.shape))
            outfile.write('# Wavelength\tCounts\n')
            np.savetxt(outfile, np.c_[spectrum_data[0], spectrum_data[1], spectrum_data[2], spectrum_data[3]], fmt='%7.9f', delimiter='\t')
        db_path = spectrum_params[0]
        date_str = spectrum_params[1]
        time_str = spectrum_params[2]
        desc_str = spectrum_params[3]
        cmt_str = spectrum_params[4]
        #self.add_spectrum_to_database(db_path, date_str, time_str, desc_str, cmt_str, path)
        return path

    def auto_load_spectrum(self, path):
        """
        Loads spectrum from file.
        :param path: path where spectrum is saved
        :return:
        """
        # Read the array from disk
        new_data = np.loadtxt(path)
        # Note that this returned a 2D array!
        return new_data

    def get_auto_path(self, base_path, identifier):
        """
        Returns an automatically generated path in format <base_path>/YYYY/<Month>/DD/<Identifier>_<uuid>
        :param base_path: Base path where data storage structure is to be set up.
        :param identifier: Denotes type of data which is stored, e.g. <Spectrum> or <Raster_Scan>
        :return: Auto-generated path in directory base_path.
        """
        local_time = time.localtime()
        year = time.strftime("%Y", local_time)
        month = time.strftime("%b", local_time)
        day = time.strftime("%d", local_time)

        # year folder
        if not os.path.exists(base_path + "/" + year):
            os.makedirs(base_path + "/" + year)
        # month folder
        if not os.path.exists(base_path + "/" + year + "/" + month):
            os.makedirs(base_path + "/" + year + "/" + month)
        # day folder
        if not os.path.exists(base_path + '/' + year + '/' + month + '/' + day):
            os.makedirs(base_path + '/' + year + '/' + month + '/' + day)
        path = '/' + year + '/' + month + '/' + day
        return path + '/' + identifier + '_' + str(uuid.uuid4()) + '.txt'

    def get_time(self):
        """
        Returns current string with local data and time.
        :return: Local date and time.
        """
        return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

    def add_spectrum_to_database(self, date, time, project, experiment, sample, desc, comments, params, pth_img, pth_spec):
        """
        Adds an entry to database for spectrum.
        :param db_path:
        :param date_str:
        :param time_str:
        :param desc_str:
        :param cmt_str:
        :param path_str:
        :return:
        """
        db = sqlite3.connect(shrd.__DB_PATH__)
        cursor = db.cursor()
        try:
            cursor.execute('''INSERT INTO spectra(date, time, project_number, experiment_number, sample_number, description,
            comments, acquisition_parameters, path_to_image, path_to_spectrum)  VALUES(?,?,?,?,?,?,?,?,?,?)''',
                           (str(date), str(time), str(project), str(experiment), str(sample), str(desc), str(comments),
                           str(params), str(pth_img), str(pth_spec)))
            print("Spectrum added to database.")
        except sqlite3.IntegrityError:
            print('Record already exists.')
        db.commit()
        db.close()

    def search_database(self, db_path):
        conn = sqlite3.connect(db_path)
        for row in conn.execute('SELECT * FROM spectra_table ORDER BY date'):
            print row






# Test scripts
def test_function():

    # generate some random data to store
    wavelength = np.empty(2000)
    counts = np.empty(2000)
    for i in range(2000):
        wavelength[i] = i
        counts[i] = np.random.rand()


    storage = StorageControl()
    db_path = storage.database_setup('./')

    spectrum_params = [db_path, '2015-01-11', '14:35:21', 'Hello', 'Comment']
    spectrum_data = np.array([wavelength, counts])

    n_files = 100
    start = time.clock()
    for i in range(n_files):
        storage.auto_store_spectrum('./', spectrum_data, spectrum_params)
    end = time.clock()
    print("Write time in total in ms: " + str((end-start)*1000))
    print("Write time per file in ms: " + str((end-start)*1000/n_files))

    storage.search_database(db_path)


if __name__ == "__main__":
   test_function()


