import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pyplot
from statsmodels.tsa.ar_model import AutoReg
from sklearn.metrics import mean_squared_error
from math import sqrt
import os

# Import the dataset with headers
cwd = os.getcwd()
# read csv using cwd
df = pd.read_csv(cwd +'/Nat_Gas.csv', header=0, delimiter=',', names=['Date', 'Price'])
# df = pd.read_csv('Documents/courses/comp432/project/Gas-Price-Estimator/Nat_Gas.csv', header=0, delimiter=',', names=['Date', 'Price'])

# Convert the date column to datetime
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')
df.head()

# Fill in missing date values
date_range = pd.date_range(start='10/31/2020', end='9/30/2024', freq='D')
missing_dates = date_range[~date_range.isin(df.index)]
data_reindexed = df.reindex(date_range)
data_filled_forward = data_reindexed.fillna(method="ffill")

# data prep
X = data_filled_forward['Price'].values
train, test = X[1:len(X)-365], X[len(X)-365:]

# model fitting
model = AutoReg(train, lags=364)
model_fit = model.fit()

# make predictions for test data
predictions = model_fit.predict(start=len(train), end=len(train)+len(test)-1, dynamic=False)
rmse = sqrt(mean_squared_error(test, predictions))

# make predictions for a year in the future
forecast = model_fit.predict(start=len(X)+1, end=len(X)+365)

# add a date range from 9/30/24 to 9/30/25 into our data
date_range = pd.date_range(start='10/31/2020', end='9/30/2025', freq='D')
data_reindexed = data_filled_forward.reindex(date_range)

# add the forecast values to the last 365 valyes to the data_filled_forward 
data_reindexed['Price'][-365:] = forecast

def valuate_contract(injection_date, withdrawal_date, max_volume=1000000, inj_with_rate=10000, storage_cost=100000):
    # injection_date is the date the gas is bought and injected into the storage facility
    # withdrawal_date is the date the gas is withdrawn from the storage facility and sold
    # max_volume is the maximum volume of gas that can be stored in the facility (units MMbtu)
    # inj_with_rate is the rate at which gas can be injected and withdrawn from the facility (per million MMbtu)
    # storage_cost is the cost of storing gas in the facility per month

    volume = max_volume

    injection_date = pd.to_datetime(injection_date)
    withdrawal_date = pd.to_datetime(withdrawal_date)

    months = len(pd.date_range(start=injection_date, end=withdrawal_date, freq='M'))
    total_storage_cost = months * storage_cost

    # prices at injection and withdrawal dates
    injection_index = data_reindexed.index.get_loc(injection_date)
    withdrawal_index = data_reindexed.index.get_loc(withdrawal_date)
    price_at_injection = data_reindexed['Price'][injection_index]
    price_at_withdrawal = data_reindexed['Price'][withdrawal_index]

    injection_withdrawal_cost = 2 * inj_with_rate/1000000 * volume
    
    total_cost = injection_withdrawal_cost + total_storage_cost + (price_at_injection * volume)

    trade_value = (price_at_withdrawal * volume) - total_cost
    
    return trade_value

while True:
    injection_date = input("Enter the injection date (yyyy-mm-dd): ")
    withdrawal_date = input("Enter the withdrawal date (yyyy-mm-dd): ")
    trade_value = valuate_contract(injection_date, withdrawal_date)
    print('Trade Value: $%.3f' % trade_value)
    if input("Do you want to continue? (y/n): ") == 'n':
        break
