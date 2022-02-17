import cv2
import os
import argparse

arguments = argparse.ArgumentParser()

arguments.add_argument("-p", "--period", required=False, help="period (for indicators)")
args = vars(arguments.parse_args())
period = 50
arg_period = args['period']
if not arg_period is None:
    period = int(arg_period)

dim= (60, 60)
for filename in os.listdir("images/"+str(period)+"/"):
    print(filename)
    image = cv2.imread("images/"+str(period)+"/" + filename)
    if image is None:
        Nones.append(image)
        continue
    if "BB.png" not in filename:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #image = cv2.resize(image,dim, interpolation = cv2.INTER_LANCZOS4)
    cv2.imwrite("images_reduced/"+str(period)+"/" + filename, image)