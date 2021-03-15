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
 
    
def get_PE_ratio(symbol_info):
    price = symbol_info['previousClose']
    latest_eps = symbol_info['trailingEps']
    if latest_eps == 0:
        return False
    else:
        return price / latest_eps
    
def do_earnings_increase_sufficiently(symbol_earnings):
    yearly_earnings = symbol_earnings[['startdatetime', 'epsactual']].dropna().groupby(['startdatetime']).sum()
    latest_3yr_avg_eps = yearly_earnings.values[-3:].sum()/3
    decade_old_3yr_avg_eps = np.array([yearly_earnings.loc[str(int(year)-10)].values[0] for year in yearly_earnings.index[-3:]]).sum()
    if latest_3yr_avg_eps > 3/2 * decade_old_3yr_avg_eps:
        return True
    else:
        return False
    
def is_PE_ratio_in_range(pe_ratio, symbol_earnings):
    yearly_earnings = symbol_earnings[['startdatetime', 'epsactual']].dropna().groupby(['startdatetime']).sum()
    latest_3yr_avg_eps = yearly_earnings.values[-3:].sum()/3
    if pe_ratio < 15 * latest_3yr_avg_eps:
        return True
    else:
        return False
    
def is_px_to_assets_in_range(symbol_info):
    price = symbol_info['previousClose'] 
    total_assets = symbol_info['totalAssets']
    book_value = symbol_info['bookValue']
    if not all([price, total_assets, book_value]):
        return False
    elif price / total_assets < 1.5 * book_value:
        return True
    else:    
        return False
    
def is_PE_ratio_x_PB_ratio_in_range(symbol_info):    
    pe_ratio = get_PE_ratio(symbol_info)
    pb_ratio = symbol_info['priceToBook']
    if not all([pe_ratio, pb_ratio]):
        return False
    elif pe_ratio * pb_ratio < 22.5:
        return True
    else:
        return False
    
def get_data_on_symbols(symbols, type_="info"):
    data = []
    symbols_with_data = []
    for symbol in symbols:
        if type_ == "info":
            try: 
                data.append(yf_info.Ticker(symbol).info)
                symbols_with_data.append(symbol)
            except: 
                continue
        elif type_ == "earnings":
            try:
                data.append(pd.DataFrame.from_dict(yf_earn.get_earnings_history(symbol)))
                symbols_with_data.append(symbol)
            except: 
                continue
        else:
            raise Exception("ERROR", "Unrecognised type_ value.")
        
    return dict(zip(symbols_with_data, data))
        

def validate_symbol(symbol, symbols_info, symbols_earnings):
    info = symbols_info[symbol]
    earnings = symbols_earnings[symbol]
    pe_ratio = get_PE_ratio(info)
    
    validations = []
    validations.append(do_earnings_increase_sufficiently(earnings))
    validations.append(is_PE_ratio_in_range(pe_ratio, earnings))
    validations.append(is_px_to_assets_in_range(info))
    validations.append(is_PE_ratio_x_PB_ratio_in_range(info))
    
    if all(validations):
        return True
    else:
        return False
      
    
if __name__ == "__main__": 
    symbols = getSAndP500List()
    symbols_info = get_data_on_symbols(symbols, type_="info")
    symbols = list(symbols_info.keys()) 
    symbols_earnings = get_data_on_symbols(symbols, type_="earnings")
    symbols = list(symbols_earnings.keys()) 
    
    shortlist = []
    for symbol in symbols:
        if validate_symbol(symbol):
            shortlist.append(symbol)
    
    print(shortlist)
        
            
        
    