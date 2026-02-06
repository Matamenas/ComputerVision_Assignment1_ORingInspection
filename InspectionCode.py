import cv2 as cv
import numpy as np
import time

from imageio import imread

def threshold(image, t):
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if img[x, y] > thresh:
                img[x, y] = 255
            else:
                img[x, y] = 0
    return img

# loop to read in each image
for i in range(1, 16):
    img = cv.imread('./ImagesToInspect/Oring' + str(i) + '.jpg', 0)
    copy = img.copy()
    thresh = 100
    bw = threshold(img, thresh)
    rgb = cv.cvtColor(bw, cv.COLOR_GRAY2RGB)

    # Text to say it Passed
    cv.putText(rgb, "PASS", (40,40), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    # Text to say it Failed
    cv.putText(rgb, "FAIL", (40, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv.imshow('thresholded image', rgb)
    cv.waitKey(0)
    cv.destroyAllWindows()
