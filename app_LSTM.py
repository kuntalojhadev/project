import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from keras.models import load_model
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

# Define date range
start = '2014-01-01'
end = '2024-01-01'

# Streamlit app title
st.title('Stock Trend Prediction')

# User input for stock ticker
user_input = st.text_input('Enter Stock Ticker', 'TSLA')

# Download data with yfinance
try:
    df = yf.download(user_input, start=start, end=end, progress=False)
except Exception as e:
    st.error(f"Failed to fetch data: {e}")
    st.stop()

# Display data
st.subheader('Data from 2014-2023')
st.write(df.describe())

# Closing Price vs Time Chart
st.subheader('Closing Price vs Time Chart')
fig = plt.figure(figsize=(12, 6))
plt.plot(df['Close'])
st.pyplot(fig)

# 100 Days Moving Averages
st.subheader('Closing Price vs Time Chart with 100MA')
ma100 = df['Close'].rolling(100).mean()
fig = plt.figure(figsize=(12, 6))
plt.plot(df['Close'], label='Closing Price')
plt.plot(ma100, label='100MA')
plt.legend()
st.pyplot(fig)

# 100 and 200 Days Moving Averages
st.subheader('Closing Price vs Time Chart with 100MA & 200MA')
ma100 = df['Close'].rolling(100).mean()
ma200 = df['Close'].rolling(200).mean()
fig = plt.figure(figsize=(12, 6))
plt.plot(df['Close'], 'b', label='Closing Price')
plt.plot(ma100, 'r', label='100MA')
plt.plot(ma200, 'g', label='200MA')
plt.legend()
st.pyplot(fig)

# Splitting Data into Training and Testing
data_training = pd.DataFrame(df['Close'][0:int(len(df) * 0.75)])
data_testing = pd.DataFrame(df['Close'][int(len(df) * 0.75):])

st.write(f'Training Data Shape: {data_training.shape}')
st.write(f'Testing Data Shape: {data_testing.shape}')

# Scaling the Data
scaler = MinMaxScaler(feature_range=(0, 1))
data_training_array = scaler.fit_transform(data_training)

# Load the model
model = load_model('keras_model.h5')

# Preparing Testing Data
past_100_days = data_training.tail(100)
final_df = pd.concat([past_100_days, data_testing], ignore_index=True)
input_data = scaler.transform(final_df)

# Creating Test Data
x_test = []
y_test = []

for i in range(100, input_data.shape[0]):
    x_test.append(input_data[i-100:i])
    y_test.append(input_data[i, 0])

x_test, y_test = np.array(x_test), np.array(y_test)

# Making Predictions
try:
    y_predicted = model.predict(x_test, verbose=0)  # Set verbose to 0 to reduce output
except Exception as e:
    st.error(f"Prediction error: {e}")
    st.stop()

scaler_factor = 1 / scaler.scale_[0]
y_predicted = y_predicted * scaler_factor
y_test = y_test * scaler_factor

# Final Graph
st.subheader('Predictions vs Original')
fig2 = plt.figure(figsize=(12, 6))
plt.plot(y_test, 'b', label='Original Price')
plt.plot(y_predicted, 'r', label='Predicted Price')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
st.pyplot(fig2)
