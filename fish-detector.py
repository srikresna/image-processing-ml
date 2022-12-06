# -*- coding: utf-8 -*-
"""PA_image_classify.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1F2wTAmpi-EvBWoFkjbFw1UirNAqTa8AZ

Informasi Pribadi

1. Nama = Sri Kresna Maha Dewa
2. Email = srikresna383@gmail.com
3. TTL = Sidoarjo, 3 Agustus 2003
4. Domisili = Sumberpucung, Malang.
5. Instansi = Politeknik Negeri Malang
"""

!pip install -q kaggle

from google.colab import files

files.upload()

!mkdir ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle datasets download -d crowww/a-large-scale-fish-dataset

!unzip a-large-scale-fish-dataset.zip

import os

os.listdir('/content/Fish_Dataset/Fish_Dataset')

print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Black Sea Sprat/Black Sea Sprat')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Black Sea Sprat/Black Sea Sprat GT')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Gilt-Head Bream/Gilt-Head Bream')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Gilt-Head Bream/Gilt-Head Bream GT')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Hourse Mackerel/Hourse Mackerel')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Hourse Mackerel/Hourse Mackerel GT')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Red Mullet/Red Mullet')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Red Mullet/Red Mullet GT')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Red Sea Bream/Red Sea Bream')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Red Sea Bream/Red Sea Bream GT')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Sea Bass/Sea Bass')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Sea Bass/Sea Bass GT')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Shrimp/Shrimp')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Shrimp/Shrimp GT')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Striped Red Mullet/Striped Red Mullet')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Striped Red Mullet/Striped Red Mullet GT')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Trout/Trout')))
print(len(os.listdir('/content/Fish_Dataset/Fish_Dataset/Trout/Trout GT')))

from pathlib import Path

dataset = Path('/content/Fish_Dataset/Fish_Dataset')

images = list(dataset.glob('**/*.png'))
labels = list(map(lambda x: os.path.split(os.path.split(x)[0])[1], images))

import pandas as pd

image = pd.Series(images).astype(str)
labels = pd.Series(labels)

df = pd.concat([image, labels], axis=1)

df.columns = ['image', 'label']
df

new_df = df[df['label'].apply(lambda x: x[-2:] != 'GT')].reset_index(drop=True)
new_df

new_df.label.value_counts()

from sklearn.model_selection import train_test_split

x_train, x_test = train_test_split(new_df, test_size=0.2,random_state=123)
#x_train, x_val = train_test_split(x_train, test_size=0.2, random_state=123)

from tensorflow.keras.preprocessing.image import ImageDataGenerator

image_data_generator = ImageDataGenerator(rescale = 1./255,
    rotation_range=40,
      width_shift_range=0.2,
      height_shift_range=0.2,
      shear_range=0.2,
      zoom_range=0.2,
      horizontal_flip=True,
      fill_mode='nearest')

train = image_data_generator.flow_from_dataframe(dataframe=x_train,
                                                 x_col='image', 
                                                 y_col='label', 
                                                 target_size=(150,150),
                                                 color_mode='rgb', 
                                                 class_mode='categorical',
                                                 shuffle=False)
test = image_data_generator.flow_from_dataframe(dataframe=x_test,
                                                x_col='image',
                                                y_col='label',
                                                target_size=(150,150), 
                                                color_mode='rgb', 
                                                class_mode='categorical', 
                                                shuffle=False)

#val = image_data_generator.flow_from_dataframe(dataframe=x_val, 
#                                               x_col='image', 
#                                               y_col='label', 
#                                               target_size=(150,150), 
#                                               color_mode='rgb', 
#                                               class_mode='categorical',
#                                               shuffle=False)

import tensorflow as tf


model = tf.keras.models.Sequential([

    tf.keras.layers.Conv2D(64, (3,3), activation = 'relu', input_shape = (150, 150, 3)),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, (3,3), activation = 'relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, (3,3), activation = 'relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, (3,3), activation = 'relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation = 'relu'),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(9, activation = 'softmax')
])

model.summary()

model.compile(optimizer="adam",
              loss='categorical_crossentropy', 
              metrics=["accuracy"])

from tensorflow.keras.callbacks import Callback, ReduceLROnPlateau, EarlyStopping

#Callback Function
class accCallback(Callback):
   def on_epoch_end(self, epoch, logs={}):
        if(logs.get('accuracy') >= 0.92 and logs.get('val_accuracy') >= 0.92):
            print("\nAccuracy and Val_Accuracy has reached 98%!", "\nEpoch: ", epoch)
            self.model.stop_training = True

callbacks = accCallback()

auto_reduction_LR = ReduceLROnPlateau(
    monitor = 'val_accuracy',
    patience = 2, #setelah 2 epoch, jika tidak ada kenaikan maka LR berkurang
    verbose = 1,
    factor = 0.2,
    min_lr = 0.000003
)

auto_stop_learn = EarlyStopping(
    monitor = 'val_accuracy',
    min_delta = 0,
    patience = 4,
    verbose = 1,
    mode = 'auto' 
)
history = model.fit(train, 
                    validation_data=test,
                    epochs=50,
                    callbacks=[callbacks, auto_reduction_LR, auto_stop_learn]
                    )

import matplotlib.pyplot as plt

pd.DataFrame(history.history).plot(figsize=(15, 5))
plt.grid(True)
plt.gca().set_ylim(0,2)

plt.show()

# Menyimpan model dalam format SavedModel
export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)

# Konversi
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('proyek-akhir-dicoding.tflite', 'wb') as f:
  f.write(tflite_model)