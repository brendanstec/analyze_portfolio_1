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

    #read in the raw data
    raw_df=pd.read_csv(filename)
    
    #drop unnecessary columns
    df=raw_df.iloc[10:].drop(['Unnamed: 32'],axis=1)
    #get and set new columns names
    new_columns = raw_df.iloc[9][0:32].tolist()
    df.columns = new_columns
    #re-format the dataframe to eliminate unnecessary rows
    length_of_df = df[df['Product Type'] == 'Total :'].index[0] - 2
    df=df.iloc[0:length_of_df - 9]
    #change index
    df.index = range(length_of_df-9)
    
    #set name of new columns
    numeric_cols = ['Last','Quantity','Market Value $','Total Cost $','Adjusted Cost $','Gain/Loss %',
	'Gain/Loss $','Dividend per share ($)','Current Yield','% of Portfolio','Est. Annual Income ($)',
	'Price Change (%)','Price Change ($)','Prior Close - Market Value ($)','Prior Close -Last($)']
    
    #remove all of the commas in the numbers in the DataFrame
    df[numeric_cols] = df[numeric_cols].replace({',':''}, regex=True)
    #change df to numeric
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    
    #replace the unreadable characters. There is a more generalized way to do this usually.
    df = df.replace({'\xca':''},regex=True)
    df = df.replace({'\xd0':''},regex=True)
    
    #get tickers
    tickers = df['Symbol']
    
   
    #fetching return data
    print ('Fetching returns data...')
    start = datetime.datetime(int(startmonth.split('_')[2]),int(startmonth.split('_')[0]),int(startmonth.split('_')[1]))
    end = datetime.datetime(int(endmonth.split('_')[2]),int(endmonth.split('_')[0]), int(endmonth.split('_')[1]) )
    
    all_data = {}
    i = 0
    for ticker in tickers:
        #print out progress to console
        i +=1
        progress = str(round(100*(i / len(tickers)),2 )) + '%'
        sys.stdout.write("\r" + progress) 
        try:
            all_data[ticker] = web.DataReader(ticker,'yahoo', start, end)
#         price = DataFrame({tic: data['Adj Close']
#                     for tic, data in all_data.iteritems()})
#         volume = DataFrame({tic: data['Volume']
#                     for tic, data in all_data.iteritems()})
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

    #add cash to the portfolio (BDPS)
    fill = [0]*len(all_data_monthly_df)
    for ticker in missing_tickers:
        all_data_monthly_df[ticker] = fill
        
    #quick function
    def annualize(r,n):
    	#r_annual = [(1 + r_period)^no_periods] - 1
    	r_annual = ((1 + r)**n) - 1
    	return r_annual
    
    #mean monthly returns of each stock
    expected_returns = np.mean(all_data_monthly_df)
    #weight of each stock in the portfolio
    weights = df['% of Portfolio'] / 100
    #expected return of portfolio
    er_port = np.dot(np.asarray(expected_returns),np.asarray(weights)) #make sure this is right
    er_port_ann = round(annualize(er_port,12),4)

    #calculate covariances between returns of stocks
    cov_matrix = all_data_monthly_df.cov()
    #calculate standard deviation of the portfolio
    port_std=round(np.sqrt(np.dot(weights.T,np.dot(cov_matrix, weights))) * np.sqrt(12),4)

    #print the output
    print ('Portfolio Annual Expected Return: ' + str(er_port_ann * 100) + '%')
    print ('Portfolio Annual Expected Standard Deviation: ' + str(port_std * 100) + '%')
    
