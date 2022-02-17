import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import load_model
import argparse

arguments = argparse.ArgumentParser()
arguments.add_argument("-n", "--new", required=False, help="y or n (train from scratch or load existing network)")
arguments.add_argument("-t", "--train", required=False, help="y or n (train or not - only predict)")


args = vars(arguments.parse_args())
from_scratch = ""
if not args['new'] is None:
    from_scratch = args['new']

img_dir = "images"
filenames = {}

for cat in os.listdir(img_dir):
    names = np.sort(os.listdir(img_dir + "/" + cat))
    filenames[cat] = names
print(filenames)
del_keys = []
for k in filenames.keys():
    if len(filenames[k]) ==0:
        del_keys.append(k)
for k in del_keys:
    del filenames[k]

##PODAJNIK DANYCH
keys = list(filenames.keys())
print("keys: ", keys)
maxi = np.max(np.array(list(map(lambda x:int(x), keys))))
print("maxi:", maxi)

filenumber = len(list(filter(lambda x:"close" in x, filenames[str(maxi)])))

channel_number =0 
for x in filenames:
    unq = set()
    for name in x:
        unq.add(name.split(";")[-1])
    channel_number += len(unq)
    if "BB.png" in unq:
        channel_number+=2
        
       
dataset = np.zeros((filenumber, 60,60, channel_number))

for filename in filenames[str(maxi)]:
    cont = False
    for key in filenames.keys():
        if filename not in filenames[key]:
            cont = True
    if cont:
        continue
    
#dopisz generowanie ratios
#ratios = np.load("ratios.npy", allow_pickle = False)
ratios = np.zeros(shape=(dataset.shape[0], 3))
##PODAJNIK DANYCH

#placeholder
model = 0
if from_scratch == "":
    inputs = keras.Input(shape=(60, 60, dataset.shape[-1]),dtype=tf.float16)
    x = layers.Conv2D(64, 3, activation="relu")(inputs)
    x = layers.Conv2D(64, 3, activation="relu")(x)
    x = layers.MaxPooling2D(3)(x)
    x = layers.Conv2D(64, 3, activation="relu")(inputs)
    x = layers.Conv2D(32, 3, activation="relu")(x)
    x = layers.MaxPooling2D(3)(x)
    x = layers.Conv2D(32, 3, activation="relu")(x)
    x = layers.Conv2D(16, 3, activation="relu")(x)
    x = layers.MaxPooling2D(3)(x)
    x = layers.Conv2D(16, 3, activation="relu")(x)
    #x = layers.Conv2D(8, 3, activation="relu")(x)
    #x = layers.MaxPooling2D(3)(x)
    x = layers.Flatten()(x)
    x = dense = layers.Dense(30, activation="relu")(x)
    x = dense = layers.Dense(10, activation="relu")(x)
    outputs = dense = layers.Dense(3)(x)
    model = keras.Model(inputs=inputs, outputs=outputs, name="algotrading")
else:
    model = keras.models.load_model('models/' + from_scratch)
    
    
model.compile(
    loss="mean_squared_error",
    optimizer=keras.optimizers.RMSprop(),
    metrics=[tf.keras.metrics.MeanSquaredError()])
model.summary()


if not args['train'] is None and args['train'] == "y":
    model.fit(dataset, ratios, batch_size=64, epochs=1, validation_split=0.2)  

print(model.predict(dataset)[-1])
    
    
        