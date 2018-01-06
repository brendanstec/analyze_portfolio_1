# analyze_portfolio_1

NOTE: this code is intended for academic use only. Past performances does not guarantee future returns. Uses all the availabiliy security price data for each security. This assumption means if ABC stock started trading 10 years ago, all 10 years of data are used to calculate
expected return/volatility. If DEF stock started trading 1 year ago in the same portfolio, only 1 year of data is used for the same calculation. Assumes reinvestment of dividends.

This code returns the expected annual return and standard deviation of a portfolio. The main function analyze_portfolio() takes in 
3 arguments as strings: filename, startmonth, and endmonth. The filename must be in csv format and is built around the formatting of
Morgan Stanley's default portfolio holdings output. Future updates to this code will allow for a more generalized formatting. See the general_example.csv file for a clear example of how to format this file. 
