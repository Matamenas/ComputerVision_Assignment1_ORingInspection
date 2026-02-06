import cv2 as cv
import numpy as np
import time
import matplotlib.pyplot as plt

from imageio import imread


# function to get histogram of an image
def createHist(image):

    # stores count of intensity value
    count = []

    # stores intensity value
    r = []

    # Loop to traverse each intensity value
    for k in range(0, 256):
        r.append(k)
        count1 = 0

        # loops to traverse each pixel in image
        for i in range(m):
            for j in range(n):
                if img[i, j]==k:
                    count1 += 1
        count.append(count1)

    return (r, count)


def threshold(image, t):
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if img[x, y] > t:
                img[x, y] = 255
            else:
                img[x, y] = 0
    return img



for i in range(1, 16):
    img = cv.imread('./ImagesToInspect/Oring' + str(i) + '.jpg', 0)

    m, n = img.shape
    r1, count1 = createHist(img)

    plt.stem(r1, count1)
    plt.xlabel('intensity value')
    plt.ylabel('number of pixels')
    plt.title('Histogram of the original image')
    plt.show()

    cv.imshow('./ImagesToInspect/Oring' + str(i) + '.jpg', img)
    cv.waitKey(0)
    cv.destroyAllWindows()

# # loop to read in each image
# for i in range(1, 16):
#     img = cv.imread('./ImagesToInspect/Oring' + str(i) + '.jpg', 0)
#     copy = img.copy()
#
#
#     thresh = 100
#     bw = threshold(img, thresh)
#     rgb = cv.cvtColor(bw, cv.COLOR_GRAY2RGB)
#
#     # Text to say it Passed
#     cv.putText(rgb, "PASS", (40,40), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
#
#     # Text to say it Failed
#     cv.putText(rgb, "FAIL", (40, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
#
#     cv.imshow('thresholded image', rgb)
#     cv.waitKey(0)
#     cv.destroyAllWindows()
