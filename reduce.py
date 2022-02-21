import cv2
import os
import argparse
import numpy as np 

arguments = argparse.ArgumentParser()

arguments.add_argument("-p", "--period", required=False, help="period (for indicators)")
arguments.add_argument("-c", "--instrument", required=False, help="cryptocurrency (BTC, ETH, ...)")
arguments.add_argument("-d", "--dim", required=False, help="images will be of size dim x dim")

args = vars(arguments.parse_args())
period = 50
arg_period = args['period']
if not arg_period is None:
    period = int(arg_period)

instrument = "BTC"
arg_instrument = args['instrument']
if not arg_instrument is None:
    instrument = arg_instrument

dim= (60, 60)
arg_dim = args['dim']
if not arg_dim is None:
    dim = (int(arg_dim),int(arg_dim))

#create folder
folder = "images_reduced/"
if not os.path.exists("images_reduced"):
    os.mkdir("images_reduced")

if not os.path.exists("images_reduced/"+str(instrument)):
    os.mkdir("images_reduced/"+str(instrument))
folder += str(instrument) + "/"

if not os.path.exists(folder + str(period)):
    os.mkdir(folder + str(period))

folder += str(period) + "/"

nones = []
for filename in np.sort(os.listdir("images/"+instrument+"/"+str(period)+"/")):
    print(filename)
    image = cv2.imread("images/"+instrument+"/"+str(period)+"/" + filename)
    if image is None:
        nones.append(image)
        continue
    if "BB.png" not in filename:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image,dim, interpolation = cv2.INTER_LANCZOS4)
    cv2.imwrite(folder + filename, image)
print("nones: ", nones)