import os
import yfinance as yf_info
import yahoo_fin.stock_info as yf_earn
import pandas as pd
import numpy as np
import pickle


def loadAPIKey():
    import quandl
    dirname = os.path.dirname(__file__) 
    filename = os.path.join(dirname, 'secrets/quandlAPIKey.txt')
    with open(filename) as f:
        quandl.ApiConfig.api_key = f.read()

def getSAndP500List():
    import bs4 as bs
    import requests
    html = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(html.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        ticker = ticker[:-1]
        tickers.append(ticker)
    return tickers    
 
    
def get_PE_ratio(symbol_info, symbol_earnings):
    price = symbol_info['previousClose']
    latest_eps = symbol_earnings['epsactual'].dropna().values[0]
    if latest_eps == 0:
        return False
    else:
        return price / latest_eps
    
def do_earnings_increase_sufficiently(symbol_earnings):
    return
    
def is_PE_ratio_in_range(pe_ratio, symbol_earnings):
    return
    
def is_px_to_assets_in_range(symbol_info):
    return
    
def is_PE_ratio_x_PB_ratio_in_range(pe_ratio, symbol_info):    
    return
    
    
    
if __name__ == "__main__": 
    symbols = getSAndP500List()[0:10]
    #symbols = ['TSCO', 'TT', 'TDG', 'TRV'] 
    
    symbols_info = [yf_info.Ticker(symbol).info for symbol in symbols]
    symbols_earnings = pd.DataFrame.from_dict(yf_earn.get_earnings_history(symbol) for symbol in symbols)
    
    print(symbols_info)    
    print(symbols_earnings)    
    
    
    