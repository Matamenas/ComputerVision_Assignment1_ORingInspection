import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from networkx.classes import neighbors
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
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            if img[i, j] < t:
                img[i, j] = 255
            else:
                img[i, j] = 0
    return img

###################################################
# 2 types of binary morphology Erosion and Dilation
# how to implement the idea:
# - similiar to the Threshold function
#

def erode(img, num_levels):
    for level in range(num_levels):
        copy = img.copy()
        neighbours = [(-1, -1), (-1, 0),(-1,1),(0,-1),(0, -1),(0,1),(1,-1),(1, 0),(1,1)]
        for i in range(1, img.shape[0]-1):
            for j in range(1, img.shape[1]-1):
                if img[i, j] == 255: # foreground pixel
                    pToErode = False
                    for y,x in neighbours:
                        if img[i+y, j+x] == 0: # background pixel
                            pToErode = True
                    if pToErode:
                        copy[i,j] = 0
        img = copy
    return copy

def dilate(img, num_levels):
    for level in range(num_levels):
        copy = img.copy()
        neighbours = [(-1, -1), (-1, 0),(-1,1),(0,-1),(0, -1),(0,1),(1,-1),(1, 0),(1,1)]
        for i in range(1, img.shape[0]-1):
            for j in range(1, img.shape[1]-1):
                if img[i, j] == 0: # foreground pixel
                    pToDilate = False
                    for y,x in neighbours:
                        if img[i+y, j+x] == 255: # background pixel
                            pToDilate = True
                    if pToDilate:
                        copy[i,j] = 255
        img = copy
    return copy

def checkNeighbours(img, i, j):
    neighbours = []
    rows, cols = img.shape
    # checking top neighbor
    if i > 0 and img[i-1, j] == 256:
        neighbours.append(img[i-1, j])
    # check left neighbor
    if j > 0 and img[i, j-1] == 256:
        neighbours.append(img[i, j-1])
    # check north-west neighbor
    if i > 0 and j > 0 and img[i-1, j-1] == 256:
        neighbours.append(img[i-1, j-1])
    # check north-east neighbor
    if i > 0 and j < cols - 1 and img[i-1, j-1] == 256:
        neighbours.append(img[i-1, j+1])
    return neighbours

def equivalence_table_post_proccessing(equivalence_table):
    keys = list(equivalence_table.keys())
    for key in keys:
        for other_key, other_value in equivalence_table.items():
            if key != other_key and key in other_value:
                equivalence_table[other_key].update(equivalence_table[key])
                equivalence_table.pop(key)
                break
    return equivalence_table

def connected_component_analysis(img):
    K = 0
    A = {}

    output_image = img.copy()

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            # if the image is part of a connected component
            if img[i, j] > 1:
                neighbors = checkNeighbours(output_image, i, j)
                if len(neighbors) == 0:
                    K += 1
                    output_image[i, j] = K
                else:
                    output_image[i, j] = min(neighbors)
                    for x in neighbors:
                        if x != output_image[i, j]:
                            if output_image[i, j] in A:
                                if x not in A[output_image[i, j]]:
                                    A[output_image[i, j]].add(x)
                            else:
                                A[output_image[i, j]] = {x}

    A = equivalence_table_post_proccessing(A)
    return output_image, A



# plot a histogram for each image
for i in range(1, 16):
    # read image in
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

    # Perform Thresholding to turn image Black Or White
    binary_img = threshold(img, t)

    # Dilate the image to remove the impurities (White parts)
    dilated_img = dilate(binary_img, 2)

    # Restore The Image to original without impurities
    eroded_img = erode(dilated_img, 2)


    cv.imshow(f"ORing {i}", binary_img)
    cv.imshow(f"Dilated {i}", dilated_img)
    cv.imshow(f"Eroded {i}", eroded_img)

    image_output = connected_component_analysis(eroded_img)

    print(image_output[1])
    key = cv.waitKey(0)
    if key & 0xFF - ord('q'):
        break
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
