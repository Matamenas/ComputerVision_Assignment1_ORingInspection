import cv2 as cv
import numpy as np
import time
import matplotlib.pyplot as plt
from imageio import imread
from scipy.signal import find_peaks


# function to get histogram of an image
def getHistValues(image):

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


# plot a histogram for each image
for i in range(1, 16):
    img = cv.imread('./ImagesToInspect/Oring' + str(i) + '.jpg', cv.IMREAD_GRAYSCALE)

    m, n = img.shape
    r1, count1 = getHistValues(img)

    # compute histogram
    counts, bin_edges = np.histogram(r1, bins=r1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # find peaks in histogram
    peaks, _ = find_peaks(count1, prominence=100)

    if len(peaks) >= 2:
        # Sort peaks by position
        sorted_peaks = sorted(peaks, key=lambda p: bin_centers[p])
        left_peak, right_peak = sorted_peaks[:2]

        # find valley index between the two peaks
        valley_index = np.argmin(count1[left_peak:right_peak]) + left_peak
        valley_x = bin_centers[valley_index]
        valley_y = count1[valley_index]
        print(f"Valley between peaks at x = {valley_x} and y = {valley_y}")

        plt.stem(r1, count1)
        plt.xlabel('intensity value')
        plt.ylabel('number of pixels')
        plt.title('Histogram of the grayscale image')
        plt.show()

        cv.imshow('./ImagesToInspect/Oring' + str(i) + '.jpg', img)
        cv.waitKey(0)
        cv.destroyAllWindows()
    else:
        print("No peaks detected")

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
