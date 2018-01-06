#NOTE: this code is intended for academic use only. Past performances does not guarantee 
#future returns. Uses all the availabiliy security price data for each security. This assumption
#means if ABC stock started trading 10 years ago, all 10 years of data are used to calculate
#expected return/volatility. If DEF stock started trading 1 year ago in the same portfolio, only
#1 year of data is used for the same calculation. 

#Inputs are strings of the file containing the portfolio holdings and start and end dates.
#Dates in format mm_dd_yyyy
#Example: analyze_portfolio('my_portfolio.csv','01_01_1990','04_30_2017')

#imports
from __future__ import division
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import bs4 as bs
import urllib
import unicodedata
import datetime
import sys
import pandas_datareader.data as web

def analyze_portfolio(filename,startmonth,endmonth):
    
	def annualize(r,n):
    #r_annual = [(1 + r_period)^no_periods] - 1
        r_annual = ((1 + r)**n) - 1
        return r_annual
	
	#read in the csv file to a dataframe
    df=pd.read_csv(filename)

    #change quantities to numeric
    df['Quantity'] = df['Quantity'].apply(pd.to_numeric, errors='coerce')

    #get rid of commas and dollar signs
    df['Name'] = df['Name'].str.replace(',', '')
    df['Name'] = df['Name'].str.replace('$', '')

    cash=float(df['Name'].iloc[len(df)-1])

    #get tickers
    tickers = df['Symbol'][:len(df)-2].tolist()
    
    #fetching return data
    print ('Fetching returns data...')
    start = datetime.datetime(int(startmonth.split('_')[2]),int(startmonth.split('_')[0]),int(startmonth.split('_')[1]))
    end = datetime.datetime(int(endmonth.split('_')[2]),int(endmonth.split('_')[0]), int(endmonth.split('_')[1]) )

    all_data = {}
    prices=list
    i = 0
    for ticker in tickers:
        #print out progress to console
        i +=1
        progress = str(round(100*(i / len(tickers)),2 )) + '%'
        sys.stdout.write("\r" + progress) 
        try:
            all_data[ticker] = web.DataReader(ticker,'yahoo', start, end)
        except:
            print "Cant find ", ticker
    
    #code to calculate monthly returns from daily price data
    all_data_monthly = {}
    data_tickers = list()
    missing_tickers = list()
    for ticker in tickers:
        if ticker not in all_data:
            #print ticker #should just be BDPS (bank deposit)
            missing_tickers.append(ticker)
        else:
            #print ticker

            data_tickers.append(ticker)
            all_data_monthly[ticker] = all_data[ticker].resample('BM', how=lambda x: x[-1])['Adj Close'].pct_change()

    #create dataframe of monthly returns
    all_data_monthly_df= pd.DataFrame(all_data_monthly)
    all_data_monthly_df = all_data_monthly_df[tickers]
    
    #add cash to the portfolio
    fill = [0]*len(all_data_monthly_df)
    all_data_monthly_df['Cash'] = fill

    
    prices=list()
    for ticker in tickers:
        prices.append(all_data[ticker]['Adj Close'][-1])

    prices = prices + [1]

    quantities = df['Quantity'][:-2].tolist()
    quantities = quantities +[cash]


    values = np.asarray(quantities) * np.asarray(prices)

    weights= values / sum(values)
    weights = weights.tolist()
    
    #mean monthly returns of each stock
    expected_returns = np.mean(all_data_monthly_df)
    #weight of each stock in the portfolio
    #weights = df['% of Portfolio'] / 100
    #expected return of portfolio
    er_port = np.dot(np.asarray(expected_returns),np.asarray(weights)) #make sure this is right
    er_port_ann = round(annualize(er_port,12),4)

    #calculate covariances between returns of stocks
    cov_matrix = all_data_monthly_df.cov()
    #calculate standard deviation of the portfolio
    port_std=round(np.sqrt(np.dot(np.asarray(weights).T,np.dot(cov_matrix, weights))) * np.sqrt(12),4)

    #print the output
    print ('Portfolio Annual Expected Return: ' + str(er_port_ann * 100) + '%')
    print ('Portfolio Annual Expected Standard Deviation: ') + str(port_std * 100) + '%'