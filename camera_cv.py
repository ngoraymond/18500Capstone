import cv2
import numpy as np
import os

import torch
import pandas as pd
import time

from Cooking_Time import Get_Time

#parameters for blob detection
params = cv2.SimpleBlobDetector_Params()
params.filterByArea = True
params.filterByConvexity = False
params.filterByColor = False
params.filterByCircularity = False

params.minArea = 1500
params.maxArea = 100000000000000000 #extremely large number, no max cap

detector = cv2.SimpleBlobDetector_create(params)
cap = cv2.VideoCapture(1)

#Shared labels
ui_cook_t = 0
ui_wid = 0

px_to_in = 55

acceptable_labels = {'Slab', 'Round', 'Blob'}

model = torch.hub.load('ultralytics/yolov5', 'custom',  path = 'best_v1.pt')

def nn_detect(image):
    #run
    results = model(image)

    #results.print()

    res_pd = results.pandas().xyxy[0]

    #print(res_pd)

    toret = 'None' 

    #get the most popular prediction
    toret_w = 0.

    for idx, row in res_pd.iterrows():
        if row['name'] in acceptable_labels:
            if row['confidence'] > toret_w:
                toret_w = row['confidence']
                toret = row['name']

    return toret

def edge_size(frame):
    #edge detect, then dilate edges
    mask = mask_make(frame, dilations=4)
    edges = cv2.Canny(mask, 0, 255)
    h, w = edges.shape[:2]

    mid_row = edges[h//2,:]

    '''
    #contours 
    contours, _ = cv2.findContours(cv2.Canny(frame, 30,255), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, (0, 0, 255), 3)

    
    cv2.imshow('edges', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return
    ''' 
    

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

    wid_in = diff/px_to_in #divide by factor to get inches

    if l_pix < 0 or r_pix < 0: #something went wrong
        print("No edge detected")
        return None
    else:
        print(f'Width: {wid_in:.4f} inches')

    return wid_in


def mask_make(frame, dilations=3): #create the black and white mask
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

    mask = cv2.dilate(mask, None, iterations=dilations) #dilate to make floodfill more effective

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

def run_cv():
    global ui_cook_t
    global ui_wid

    ret, frame = cap.read()
    mask = mask_make(frame)

    '''
    cv2.imshow('mask', mask)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return
    '''

    #detect blobs
    blobs = detector.detect(mask)

    if len(blobs) > 0:
        #print(len(blobs), " objects detected")
        print('object(s) detected')

        #other work here, sending instructions to robot arm

        #classify image
        labels = nn_detect(frame)
        wid = None

        #depending on classification, use edges to determine size of object
        if labels == 'Slab':
            wid = edge_size(frame)
            if wid == None:
                return ui_cook_t, ui_wid
            ui_wid = str(wid)
        elif labels in acceptable_labels:
            ui_wid = "N/A"

        if labels in acceptable_labels:
            cook_t = Get_Time(labels, wid)
            ui_cook_t = cook_t

    return ui_cook_t, ui_wid

def run_loop():
    while True:
        run_cv()

if __name__ == '__main__':
    #cuda check
    print(torch.version.cuda)
    print(torch.cuda.is_available())
    run_loop()