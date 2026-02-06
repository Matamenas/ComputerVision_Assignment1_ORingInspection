import cv2 as cv
import numpy as np
import time
import matplotlib.pyplot as plt
from imageio import imread
from scipy.signal import find_peaks


# function to get histogram of an image
def getHistValues(image):

    # get image shape
    m, n = image.shape

    # stores count of intensity value
    count = []

    # stores intensity value
    r = []

    # Loop to traverse each intensity value
    for k in range(-10, 280):
        r.append(k)
        count1 = 0

        # loops to traverse each pixel in image
        for i in range(m):
            for j in range(n):
                if img[i, j]==k:
                    count1 += 1
        count.append(count1)

    return (r, count)

# Automatic threshold from histogram valley
def findValleyThreshold(hist, peaks):

    peaks = sorted(peaks)

    left_peak = peaks[0]
    right_peak = peaks[1]

    print(left_peak)
    print(right_peak)

    valley = np.argmin(hist[left_peak:right_peak]) + left_peak
    return valley


def threshold(image, t):
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if img[x, y] > t:
                img[x, y] = 255
            else:
                img[x, y] = 0
    return img


# plot a histogram for each image
for i in range(1, 16):
    img = cv.imread('./ImagesToInspect/Oring' + str(i) + '.jpg', 0)
    copy = img.copy()

    r, hist = getHistValues(copy)

    max_height = max(hist)
    prominence = 0.01 * max_height

    # find peaks in histogram
    peaks, _ = find_peaks(hist, prominence=prominence)

    if len(peaks) < 2:
        print(f"Image {i}:  No Clear Bimodal Histogram")
        continue

    plt.stem(r, hist)
    plt.xlabel('intensity value')
    plt.ylabel('number of pixels')
    plt.title('Histogram of the grayscale image')
    plt.show()

    t = findValleyThreshold(hist, peaks)

    print(f"Image {i}:  Automatic Threshold = {t}")

    binary_img = threshold(img, t)

    cv.imshow(f"ORing {i}", binary_img)
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
