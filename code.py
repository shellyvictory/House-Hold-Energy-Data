# -*- coding: utf-8 -*-
"""Shelly Victory_Second Project

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uie2WUfThMPgC9_fyp7bkBySVh2khfxx

Nama: Shelly Victory;
User Name: victorysl;
Alamat Email: shellyvicotry92@gmail.com;
Dataset source: https://www.kaggle.com/jaganadhg/house-hold-energy-data
"""

import numpy as np
from tensorflow.keras.models import Sequential
from keras.layers import Dense, LSTM, Flatten, Activation
from keras.callbacks import ReduceLROnPlateau
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf

import os
os.listdir('sample_data')
import pandas as pd
data = pd.read_csv('sample_data/data.csv')
del data ['NOTES']
data.tail()

data.head()

# identify unique data based on its date
pd.Series(data['DATE'].unique()).sort_index(ascending=True)

data1 = pd.date_range('2016-10-22', '2018-10-24', freq='D').to_series()
data1.dt.dayofweek # The number of unique columns on df = number of date range from the beginning until the end

data.isnull().sum()

data.dtypes

import matplotlib.pyplot as plt
x = data['DATE'].values
y = data['USAGE'].values

plt.figure(figsize=(15,5))
plt.plot(x, y)
plt.xlabel('Date',size=10)
plt.ylabel('Usage',size=20)
plt.title('Consumption in kWh',
          fontsize=18);

# membagi dataset
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=False)

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
  series = tf.expand_dims(series, axis=-1)
  data = tf.data.Dataset.from_tensor_slices(series)
  data = data.window(window_size + 1, shift=1, drop_remainder=True)
  data = data.flat_map(lambda w:w.batch(window_size + 1))
  data = data.shuffle(shuffle_buffer)
  data = data.map(lambda w: (w[:-1], w[-1:]))
  return data.batch(batch_size).prefetch(1)

train_set = windowed_dataset(y_train, window_size=60, batch_size=100, shuffle_buffer=1000)

validation_set = windowed_dataset(y_test, window_size=60, batch_size=100, shuffle_buffer=10000)

from keras.layers import Conv1D
model=Sequential([
  Conv1D(filters=60, kernel_size=5, activation='relu', input_shape=[None, 1]),                
  LSTM(128, return_sequences=True),
  LSTM(64, return_sequences=False),
  Flatten(),
  Dense(32, activation="relu"),
  Dense(32, activation="relu"),
  Dense(units=1)
])

optimizer = tf.keras.optimizers.SGD(learning_rate=1.0000e-04, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

reduce = ReduceLROnPlateau(monitor='loss', patience=3, factor=0.2, learning_rate=1.0000e-04)
history = model.fit(train_set, epochs=5, validation_data=validation_set, callbacks=[reduce])