import cv2
import numpy as np
import os

import torch
import pandas as pd

#parameters for blob detection
params = cv2.SimpleBlobDetector_Params()
params.filterByArea = True
params.filterByConvexity = False
params.filterByColor = False
params.filterByCircularity = False

params.minArea = 1500
params.maxArea = 100000000000000000 #extremely large number, no max cap

model = torch.hub.load('ultralytics/yolov5', 'custom',  path = 'best.pt')

def nn_detect(image):
    #run
    results = model(image)

    #get name of first result, return it
    results.print()

    res_pd = results.pandas().xyxy[0]

    toret = 'None' if res_pd.name.empty else res_pd.name[0]

    return toret

def edge_size(mask):
    #edge detect, then dilate edges
    edges = cv2.Canny(mask, 0, 255)
    h, w = mask.shape[:2]

    mid_row = edges[h//2,:]

    #find the rightmost pixel left of center and the leftmost pixel right of center
    l_pix = -1
    r_pix = -1

    for col, px in enumerate(mid_row):
        if px == 255 and col < w//2:
            l_pix = col
        
        if px == 255 and r_pix == -1 and col > w//2:
            r_pix = col
            break

    diff = r_pix - l_pix #pixel difference
    px_to_in = 127 

    wid_in = diff/px_to_in #divide by factor to get inches

    if l_pix < 0 or r_pix < 0: #something went wrong
        print("No edge detected")
    else:
        print(f'{wid_in:.2f} inches')


def mask_make(frame): #create the black and white mask
    #convert image of floating food into HSV, to threshold

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # lower mask
    lower_red = np.array([0,70,50])
    upper_red = np.array([10,255,255])
    mask0 = cv2.inRange(frame, lower_red, upper_red)

    # upper mask
    lower_red = np.array([178,70,50])
    upper_red = np.array([180,255,255])
    mask1 = cv2.inRange(frame, lower_red, upper_red)

    mask = (mask0+mask1)

    mask = cv2.dilate(mask, None, iterations=3) #dilate to make floodfill more effective

    mask_flood = mask.copy()

    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h, w = mask.shape[:2]
    extra_w = np.zeros((h+2, w+2), np.uint8)

    # Floodfill from point (0, 0)
    cv2.floodFill(mask_flood, extra_w, (0,0), 255)

    # Invert floodfilled image
    mask_flood_inv = cv2.bitwise_not(mask_flood)

    # Combine the two images to get the foreground.
    mask = mask | mask_flood_inv
    
    return mask

def run_loop():
    cap = cv2.VideoCapture(0)
    detector = cv2.SimpleBlobDetector_create(params)
    while True:
        ret, frame = cap.read()
        mask = mask_make(frame)

        '''
        cv2.imshow('mask', mask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        '''

        #detect blobs
        blobs = detector.detect(mask)

        if len(blobs) > 0:
            print(len(blobs), " objects detected")

            #other work here, sending instructions to robot arm

            #classify image
            labels = nn_detect(frame)

            #depending on classification, use edges to determine size of object
            if labels == 'slab':
                edge_size(mask)

if __name__ == '__main__':
    run_loop()