__author__ = 'df-setup-basement'

import matplotlib.pyplot as plt


import MMCorePy
import cv2


mmc = MMCorePy.CMMCore()
mmc.loadDevice('ThorCam', 'ThorlabsUSBCamera', 'ThorCam')
mmc.initializeDevice('ThorCam')
mmc.setCameraDevice('ThorCam')

cv2.namedWindow('Video', cv2.CV_WINDOW_AUTOSIZE)
mmc.startContinuousSequenceAcquisition(1)
while True:
    rgb32 = mmc.getLastImage()
    if mmc.getRemainingImageCount() > 0:
         # rgb32 = mmc.popNextImage()
        rgb32 = mmc.getLastImage()
        # Efficient conversion without data copying.
        # bgr = rgb32.view(dtype=np.uint8).reshape(
        #     rgb32.shape[0], rgb32.shape[1], 4)[..., :3]
        cv2.imshow('Video', rgb32)
    else:
        print('No frame')
    if cv2.waitKey(20) >= 0:
        break
cv2.destroyAllWindows()
mmc.stopSequenceAcquisition()
mmc.reset()


