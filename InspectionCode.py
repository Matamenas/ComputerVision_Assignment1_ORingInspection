import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import time


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

    # get list of peaks sorted in ascending order
    peaks = sorted(peaks)

    # get the smaller peak and larger peak
    left_peak = peaks[0]
    right_peak = peaks[1]

    # print them to screen
    print(left_peak)
    print(right_peak)

    # slice the histogram into 2 parts left peak (inclusive) and right peak (exclusive)
    # using numpy I can get the minimum values index and then just add the left peak to the slice and minimum value
    valley = np.argmin(hist[left_peak:right_peak]) + left_peak
    return valley


def threshold(img, t):
    # use a binary copy of the image to threshold
    binary = np.zeros_like(img)

    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            if img[i, j] < t:
                binary[i, j] = 255
            else:
                binary[i, j] = 0
    return binary

###################################################
# 2 types of binary morphology Erosion and Dilation
# how to implement the idea:
# - similiar to the Threshold function
#

def erode(img, num_levels):
    for level in range(num_levels):
        copy = img.copy()
        # capture all neighbors
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
                if img[i, j] == 0: # background pixel
                    pToDilate = False
                    for y,x in neighbours:
                        if img[i+y, j+x] == 255: # foreground pixel
                            pToDilate = True
                    if pToDilate:
                        copy[i,j] = 255
        img = copy
    return copy

# Method to check for neighbors in connected component labeling
# takes in image and the current pixel location
def checkNeighbours(img, i, j):
    neighbours = []
    rows, cols = img.shape
    # checking top neighbor
    if i > 0 and img[i-1, j] != 256:
        neighbours.append(img[i-1, j])
    # check left neighbor
    if j > 0 and img[i, j-1] != 256:
        neighbours.append(img[i, j-1])
    # check north-west neighbor
    if i > 0 and j > 0 and img[i-1, j-1] != 256:
        neighbours.append(img[i-1, j-1])
    # check north-east neighbor
    if i > 0 and j < cols - 1 and img[i-1, j+1] != 256:
        neighbours.append(img[i-1, j+1])
    return neighbours

# method to be used for connected component labeling (CCL) after finding regions
# essentialy here we just group the labels into equivalency classes (and later we assign each object with its corresponding label)
# if there was more than one object it would get its own class aswell
def equivalence_table_post_proccessing(equivalence_table):
    keys = list(equivalence_table.keys())
    for key in keys:
        for other_key, other_value in equivalence_table.items():
            if key != other_key and key in other_value:
                equivalence_table[other_key].update(equivalence_table[key])
                equivalence_table[other_key].update([other_key])
                equivalence_table.pop(key)
                break
    return equivalence_table

# first scan of the image to label all white pixels
def connected_component_analysis(img):
    K = 0
    A = {}

    output_image = np.ones(shape=img.shape) * 256

    # iterate over each pixel in the image
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):

            # check if pixel is part of a connected component
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

# second scan to group all labels what were added from the first scan
def group_pixels(label_img, equivalency_table):

    # lets create a mapping from every equivalent label to its smallest label
    label_map = {}

    # now i call the equivalency table from the first scan
    # because we need to group all labels
    for key, value_set in equivalency_table.items():
        smallest = min([key] + list(value_set))
        label_map[key] = smallest
        for v in value_set:
            label_map[v] = smallest

    # and now i apply the mapping to the image
    rows, cols = label_img.shape

    for i in range(rows):
        for j in range(cols):
            if label_img[i, j] in label_map:
                label_img[i, j] = label_map[label_img[i, j]]
    return label_img

# method to calculate the perimeter of each O-Ring
# this will allow for easier calculation of circularity of O-Ring later
def compute_perimeter(img):

    perimeter = 0
    rows, cols = img.shape

    # count the pixel boundaries
    for i in range(1, rows-1):
        for j in range(1, cols-1):
            if img[i, j] == 255:
                # check edges if the surrounding pixels are black it's an edge pixel
                # so add perimeter to 1 (we need only check left, right, and top, should work universaly)
                if img[i - 1, j] == 0 or img[i + 1, j] == 0 or img[i, j + 1] == 0:
                    perimeter +=1

    return perimeter



# plot a histogram for each image
for z in range(1, 16):

    # start time
    start = time.time()

    # read image in
    img = cv.imread('./ImagesToInspect/Oring' + str(z) + '.jpg', 0)
    copy = img.copy()

    # get the histogram values (pixels and intensity)
    r, hist = getHistValues(copy)

    # dynamically get the max height of each histogram
    # and then get 1% of that height to be the prominence (it just works)
    max_height = max(hist)
    prominence = 0.01 * max_height

    # find peaks in histogram
    peaks, _ = find_peaks(hist, prominence=prominence)

    if len(peaks) < 2:
        print(f"Image {z}:  No Clear Bimodal Histogram")
        continue

    plt.stem(r, hist)
    plt.xlabel('intensity value')
    plt.ylabel('number of pixels')
    plt.title('Histogram of the grayscale image')
    plt.show()

    t = findValleyThreshold(hist, peaks)

    print(f"Image {z}:  Automatic Threshold = {t}")

    # Perform Thresholding to turn image Black Or White
    binary_img = threshold(img, t)

    print("Unique Values in binary image", np.unique(binary_img))

    # Dilate the image to remove the impurities (Black Parts)
    dilated_img = dilate(binary_img, 2)

    # Restore The Image to original without impurities
    eroded_img = erode(dilated_img, 2)

    # First Scan of the image for connected component labeling
    image_output = connected_component_analysis(eroded_img)

    print(image_output[1])

    # second scan of the image and grouping of pixels
    label_img = group_pixels(image_output[0], image_output[1])

    # now i must extract Largest Component in the image
    unique, counts = np.unique(label_img, return_counts=True)
    label_sizes = dict(zip(unique, counts))
    label_sizes.pop(256, None)
    label_sizes.pop(0, None)

    print("Unique values in o_ring after extracting largest component", np.unique(label_img))

    print("Label sizes:", label_sizes)

    largest_label = max(label_sizes, key=label_sizes.get)
    print("Largest Label:", largest_label)
    #################################################################

    # Now create a clean O-Ring Mask by keeping only the largest component (The O-Ring 255)
    o_ring = np.zeros_like(label_img)

    for i in range(label_img.shape[0]):
        for j in range(label_img.shape[1]):
            if label_img[i,j] == largest_label:
                o_ring[i,j] = 255

    print("Unique values in o_ring after filling largest component", np.unique(o_ring))

    # now that i have my O-Ring shape and sizes i can get the area
    area = np.sum(o_ring == 255)

    print(f"Area of Image {z} = {area}")

    # let's get the perimeter of the ring
    perimeter = compute_perimeter(o_ring)

    print(f"Perimeter of Image {z} = {perimeter}")

    # To compute circularity of a Ring there is a formula
    # C = (4pi * Area) / (Perimeter^2)
    # with this I should be able to determine whether the O-Ring is flawed or not
    circularity = (4 * np.pi * area) / (perimeter ** 2)

    print(f"Circularity of Image {z} = {circularity}")

    # If the image is under a certain threshold of circularity it will be a fail
    if circularity < 0.30:
        result = "FAIL"
    else:
        result = "PASS"

    # show the images one by one to show process
    cv.imshow(f"Thresholded ORing {z}", binary_img)
    cv.imshow(f"Dilated {z}", dilated_img)
    cv.imshow(f"Eroded {z}", eroded_img)
    cv.imshow(f"Connected O-Ring {z}", o_ring)

    rgb = cv.cvtColor(binary_img, cv.COLOR_GRAY2RGB)

    # Text to say it Passed
    if result == "PASS":
        cv.putText(rgb, "PASS", (15,40), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    else:
        # Text to say it Failed
        cv.putText(rgb, "FAIL", (15, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # end timer
    end = time.time()

    # total time taken
    total_time = end - start

    # Show Final result
    cv.putText(rgb, f" {total_time:.2f} Secs", (1, 215), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv.imshow(f"Final Inspected Image {z}", rgb)

    key = cv.waitKey(0)
    if key & 0xFF - ord('q'):
        break
    cv.destroyAllWindows()
