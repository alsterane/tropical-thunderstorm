__author__ = 'df-setup-basement'

import ctypes
from holograms.SimplePhaseGrating import *
import cv2
import time

# control MadCityLabs Piezo Stage through Madlib.dll
class MeadowlarkCommunication:
    """
    .. module:: MeadowlarkCommunication
    :platform: Windows
    :synopsis: Module to communicate with the meadowlark liquid crystal optical modulators (LCOM/SLM). Uses the
    512PCIe16Board.dll to communicate via 16 bit PCIe interface card.
    .. moduleauthor:: lh
    """

    def __init__(self):
        lib = ctypes.WinDLL('PCIe16Interface.dll')

        # int Constructor(int LCType)
        self.constructor = lib['Constructor']

        # void Deconstructor()
        self.deconstructor = lib['Deconstructor']

        # void SLMPower(int Board, bool PowerOn)
        self.setSLMPower = lib['SLMPower']

        # bool GetSLMPower(int Board)
        self.getSLMPower = lib['GetSLMPower']

        # void ReadTIFF(const char* FilePath, unsigned short* ImageData,
        # unsigned int ScaleWidth, unsigned int ScaleHeight)
        self.readTiff = lib['ReadTIFF']

        # void WriteImage(int board, unsigned short* Image)
        self.writeImage = lib['WriteImage']

        # void SetTrueFrames(int Board, int TrueFrames)
        self.setTrueFrames = lib['SetTrueFrames']

        # void LoadSequence (int Board, unsigned short* Images, int NumberOfImages)
        self.loadSequence = lib['LoadSequence']

        # void SetSequenceRate (double FrameRate)
        # cannot find this function
        #self.setSequenceRate = lib['SetSequenceRate']

        # void StartSequence()
        self.startSequence = lib['StartSequence']

        # void StopSequence()
        self.stopSequence = lib['StopSequence']

    def initialise_slm(self, lcType):
        """
        Initialises the spatial light modulator

        :param int Liquid crystal type (0 = FLC, 1 = Nematic).
        :return int Number of board found.
        """
        try:
            num = self.constructor(lcType)
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
        try:
            self.set_slm_power(board_num, 0)
            self.deconstructor()
        except:
            raise Exception("Could not properly shut down.")


    def set_slm_power(self, board_num, is_on):
        """
        Turn on or off SLMs connected to specified board.

        :param boardNum: int Number of board.
        :param isOn: bool Specify whether board is turned on or off.
        """
        try:
            self.setSLMPower(ctypes.c_int(board_num), ctypes.c_bool(is_on))
        except:
            raise Exception("Could not turn on SLM.")

    def get_slm_power(self, board_num):
        """
        Check whether SLM with specified board number is on or off

        :param boardNum: int Number of board.
        :return bool Status of SLM (False=Off, True=On).
        """
        try:
            status = self.getSLMPower(ctypes.c_int(board_num))
        except:
            raise Exception("Could not verify status of SLM.")
        return status

    def read_image(self,  scale_width, scale_height):
        """
        Read image from disk into buffer.

        :param file_path: const char Path to file to load.
        :param image_data: unsigned short Pointer to buffer which holds image data.
        :param scale_width: int Image width (either 256 px or 512 px).
        :param scale_height: int Image height (either 256 px or 512 px).
        """
        # FIXME: this still does not work. need to create & pass one character string
        path = "C:\\PCIe16C++SDK\\Image_Files\\16Astigx.tiff"
        cpath = ctypes.c_char(list(path))

        dim = scale_width*scale_height
        self.image = (ctypes.c_ushort * dim)()
        self.readTiff(ctypes.pointer(cpath), ctypes.pointer(self.image), ctypes.c_uint(scale_width), ctypes.c_uint(scale_height))

    def write_image(self, board_num, array):
        """
        Writes image to specified board.

        :param board_num: int Board number to write data to.
        :param numpy_array: unsigned short array to write to SLM.
        """
        arr = (ctypes.c_ushort * len(array))(*array)
        self.writeImage(board_num, ctypes.pointer(arr))

    def set_true_frames(self, board_num, frames):
        """
        This function sets the value of True Frames for all connected PCIe 16 boards.
        The value of True Frames determines how fast the SLM toggles between the true and the inverse image
        (a necessary procedure that is done to DC balance the SLM).

        :param board_num: int Board number.
        :param frames: int Number of frames.
        """
        self.setTrueFrames(ctypes.c_int(board_num), ctypes.c_int(frames))

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
        arr = (ctypes.c_ushort * len(images))(*images)
        try:
            self.loadSequence(board_num, ctypes.byref(arr), num_images)
        except:
            raise Exception("Image sequence could not be loaded.")

    def start_sequence(self):
        """
        Start loaded image sequence.
        """
        try:
            self.startSequence()
        except:
            raise Exception("Sequence cannot be started.")
    def stop_sequence(self):
        """
        Stop loaded image sequence.
        """
        try:
            self.stopSequence
        except:
            raise Exception("Sequence cannot be stopped.")


# code to test the class above
def main():
    bnc = MeadowlarkCommunication()
    num = bnc.initialise_slm(1)
    print num
    bnc.set_true_frames(0, 3)
    bnc.set_slm_power(0, True)


    print "Trying to generate and write an array to the SLM"
    grating = SimplePhaseGrating()
    array = []
    for i in range(50):
        array.append(grating.createOneDTestArray(4.0*(i+1.0)))

    for i in range(50):
        bnc.write_image(0, array[i])
        time.sleep(0.5)

    bnc.shutdown_slm(0)

if  __name__ =='__main__':main()