__author__ = 'df-setup-basement'

from ctypes import windll, c_int, c_char, byref, pointer, c_float, c_char_p, c_long, c_bool, c_uint, c_ushort
import ctypes
from holograms.SimplePhaseGrating import *
import platform
import os
import time


class MeadowlarkCommunication:
    """
    .. module:: MeadowlarkCommunication
    :platform: Windows
    :synopsis: Module to communicate with the meadowlark liquid crystal optical modulators (LCOM/SLM). Uses the
    512PCIe16Board.dll to communicate via 16 bit PCIe interface card.
    .. moduleauthor:: lh
    """


    def __init__(self):
        if platform.system() == "Windows":
            try:
                current = os.getcwd()
                os.chdir("C:\\Users\\df-setup-basement\\PycharmProjects\\Equipment\\equipment\\modulators\\")
                self._dll = windll.LoadLibrary('PCIe16Interface.dll')
                os.chdir(current)
            except:
                raise Exception("Failed to load Meadowlark DLL. Please check specified path.")


        #err = self._dll.GetCameraSerialNumber(byref(serial))
        #lib = ctypes.WinDLL('PCIe16Interface.dll')

        # int Constructor(int LCType)
        #self.constructor = lib['Constructor']

        # void Deconstructor()
        #self.deconstructor = lib['Deconstructor']

        # void SLMPower(int Board, bool PowerOn)
        #self.setSLMPower = lib['SLMPower']

        # bool GetSLMPower(int Board)
        #self.getSLMPower = lib['GetSLMPower']

        # void ReadTIFF(const char* FilePath, unsigned short* ImageData,
        # unsigned int ScaleWidth, unsigned int ScaleHeight)
        #self.readTiff = lib['ReadTIFF']

        # void WriteImage(int board, unsigned short* Image)
        #self.writeImage = lib['WriteImage']

        # void SetTrueFrames(int Board, int TrueFrames)
        #self.setTrueFrames = lib['SetTrueFrames']

        # void LoadSequence (int Board, unsigned short* Images, int NumberOfImages)
        #self.loadSequence = lib['LoadSequence']

        # void SetSequenceRate (double FrameRate)
        # cannot find this function
        #self.setSequenceRate = lib['SetSequenceRate']

        # void StartSequence()
        #self.startSequence = lib['StartSequence']

        # void StopSequence()
        #self.stopSequence = lib['StopSequence']

    def initialise_slm(self, lc_type):
        """
        Initialises the spatial light modulator

        :param int Liquid crystal type (0 = FLC, 1 = Nematic).
        :return int Number of board found.
        """
        try:
            num = self._dll.Constructor(lc_type)
        except:
            raise Exception("Initialisation failed.")
        return num

    def shutdown_slm(self, board_num):
        """
        This function is responsible for closing communication with the hardware, and for properly shutting down
        the hardware. This should always be the last BNS function that the user calls.
        It is very import that this function be called before exiting the software to prevent accidental
        catastrophic hardware damage.

        :param board_num: int Board number of SLM which shall be shut down.
        """
        #try:
        #if self.get_slm_power(board_num):
        #    self.set_slm_power(board_num, 0)
        self._dll.Deconstructor()
        #except:
            #raise Exception("Could not properly shut down.")


    def set_slm_power(self, board_num, is_on):
        """
        Turn on or off SLMs connected to specified board.

        :param boardNum: int Number of board.
        :param isOn: bool Specify whether board is turned on or off.
        """
        board_num += 1       # board num for this function is a 1 based index, i.e. starts at 1
        self._dll.SLMPower(c_int(board_num), c_bool(is_on))


    def get_slm_power(self, board_num):
        """
        Check whether SLM with specified board number is on or off

        :param boardNum: int Number of board.
        :return bool Status of SLM (False=Off, True=On).
        """
        board_num += 1       # board num for this function is a 1 based index, i.e. starts at 1
        status = self._dll.GetSLMPower(c_int(board_num))
        return status

    def set_lut(self, board_num, lut_index):
        #board_num += 1
        #lut_path = path.encode('utf-8')
        #buf = ctypes.create_string_buffer(lut_path)
        print os.getcwd()
        print board_num
        if lut_index == 0:
            self._dll.LoadLUTFile(c_int(0), c_char_p('./slm3404_at532_P16.lut'))
        elif lut_index == 1:
            self._dll.LoadLUTFile(c_int(0), c_char_p('./slm3404_at635_P16.lut'))
        elif lut_index == 2:
            status = self._dll.LoadLUTFile(c_int(0), c_char_p('./slm3404_at785_P16.lut'))
            print status
        elif lut_index == 3:
            status = self._dll.LoadLUTFile(c_int(0), c_char_p('./linear.lut'))
            print status
        elif lut_index == 4:
            status = self._dll.LoadLUTFile(c_int(0), c_char_p('./half.lut'))
            print status

    def read_image(self, path, scale_width, scale_height):
        """
        Read image from disk into buffer.

        :param path: const char Path to file to load.
        :param scale_width: int Image width (either 256 px or 512 px).
        :param scale_height: int Image height (either 256 px or 512 px).
        :return: image
        """
        tiff_path = path.encode('utf-8')
        buf = ctypes.create_string_buffer(tiff_path)

        dim = scale_width*scale_height
        image = (c_ushort * dim)()
        self._dll.ReadTIFF(buf, byref(image), c_uint(scale_width), c_uint(scale_height))
        return image

    def write_image(self, board_num, array):
        """
        Writes image to specified board.

        :param board_num: int Board number to write data to.
        :param numpy_array: unsigned short array to write to SLM.
        """
        board_num += 1      # 1 based index
        print np.shape(array)
        if len(np.shape(array)) == 2:      # if 2D array, then convert into line
            tmp = np.empty((np.size(array, 0)*np.size(array, 1)), dtype=np.uint16)
            for i in range(np.size(array, 0)):
                for j in range(np.size(array, 1)):
                    tmp[i + j*np.size(array, 1)] = array[i][j]
            arr = (c_ushort * len(tmp))(*tmp)
            print np.shape(tmp)
            self._dll.WriteImage(board_num, byref(arr))
        else:
            arr = (c_ushort * len(array))(*array)
            self._dll.WriteImage(board_num, byref(arr))


    def set_true_frames(self, board_num, frames):
        """
        This function sets the value of True Frames for all connected PCIe 16 boards.
        The value of True Frames determines how fast the SLM toggles between the true and the inverse image
        (a necessary procedure that is done to DC balance the SLM).

        :param board_num: int Board number.
        :param frames: int Number of frames.
        """
        board_num += 1      # 1 based index
        self._dll.SetTrueFrames(c_int(board_num), c_int(frames))


    # FIXME: does find this function in library!! despite manual claiming it exists?
    # def set_sequence_rate(self, framerate):
    #     """
    #     Rate at which software sequences through a set of images.
    #     :param framerate: double Frame rate in Hz at which the software sequences through a loaded set of sequences.
    #     """
    #     try:
    #         self.setSequenceRate(ctypes.c_double(framerate))
    #     except:
    #         raise Exception("Frame rate can not be adjusted.")

    def load_sequence(self, board_num, images, num_images):
        """
        This function loads a sequence of images to the PCIe controller memory.

        :param board_num: int Number of the board to affect.
        :param images: Numpy array of image data to load to the SLM. Should be a 1xN array where
        N is the number of images * number of pixels.
        :param num_images: int Number of images to load.
        """

        # convert numpy array to unsigned short
        arr = (c_ushort * len(images))(*images)
        try:
            self._dll.LoadSequence(board_num, byref(arr), num_images)
        except:
            raise Exception("Image sequence could not be loaded.")

    def start_sequence(self):
        """
        Start loaded image sequence.
        """
        try:
            self._dll.StartSequence()
        except:
            raise Exception("Sequence cannot be started.")

    def stop_sequence(self):
        """
        Stop loaded image sequence.
        """
        try:
            self._dll.StopSequence()
        except:
            raise Exception("Sequence cannot be stopped.")


# code to test the class above
def main():
    #bnc = MeadowlarkCommunication()
    #num = bnc.initialise_slm(1)
    #print num
    #print bnc.get_slm_power(num)
    #print bnc.set_slm_power(num, True)
    #bnc.set_true_frames(0, 3)
    #bnc.set_slm_power(0, True)

    grating = SimplePhaseGrating()
    array = []
    for i in range(1):
        array.append(grating.createOneDTestArray(4.0*(i+1.0)))

    for i in range(1):
        #bnc.write_image(0, array[i])
        time.sleep(0.5)

    #print("images written")
    #print bnc.get_slm_power(num)
    #bnc.set_slm_power(2, 1)
    #print bnc.get_slm_power(num)
    #print ("now shutting down")
    #bnc.set_slm_power(2, 0)
    #bnc.shutdown_slm(num)

    arr = np.empty((5))
    print len(np.shape(arr))

if  __name__ =='__main__':main()