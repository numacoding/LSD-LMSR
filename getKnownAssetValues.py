import math
from getAssetData import getVolumeData
import pandas as pd
from datetime import datetime, date, timedelta
from scipy.stats import pearsonr
import json
import numpy as np
import random
import time
from tqdm import tqdm

today = date.today().strftime('%Y-%m-%d')
with open('apikey.json') as json_file:
    key = json.load(json_file)

apiKey = list(key.values())[0]

def getDateAndCorrelation(exchange, symbol1, symbol2, resolution, initialDate, endDate, apiKey):
    initDate = datetime.strptime(initialDate, "%Y-%m-%d")
    finishDate = datetime.strptime(endDate, "%Y-%m-%d")

    datePeriod= pd.date_range(initDate,finishDate, freq='D')
    volumeTicket1 = getVolumeData(exchange, symbol1, resolution, initialDate, endDate, apiKey)
    volumeTicket2 = getVolumeData(exchange, symbol2, resolution, initialDate, endDate, apiKey)
    
    suffix1 = f'_{symbol1}'
    suffix2 = f'_{symbol2}'
    dataFrameTickets = volumeTicket1.merge(volumeTicket2, how='inner', 
                                        left_index=True, right_index=True, 
                                        suffixes=[suffix1, suffix2])

    correlation = pearsonr(dataFrameTickets[f'close_price{suffix1}'], dataFrameTickets[f'close_price{suffix2}'])
    lastVolSym1 = volumeTicket1['volume'][-1]
    lastVolSym2 = volumeTicket2['volume'][-1]
    return dataFrameTickets, correlation[0], lastVolSym1, lastVolSym2

initialDate = '2020-01-01'

df, correlation, lastVolBUSD, lastVolBNB = getDateAndCorrelation(exchange= 'BINANCE', symbol1= symbol1, symbol2= symbol2, resolution= 'D', initialDate = initialDate, endDate = today, apiKey = apiKey)



#calculate the correlation between both of them and define a base fee
tokenCorrelation = correlation
if tokenCorrelation>=0.95:
    print(f'Our correlation coefficient is {tokenCorrelation}. We are dealing with similar assets')
    riskLevel = 0
    fee = 0.003
    minFee = 0.002
    maxFee = 0.006
elif tokenCorrelation >=0.85:
    print(f'Our correlation coefficient is {tokenCorrelation}. We are dealing with highly correlated assets')
    riskLevel = 1
    fee = 0.01
    minFee = 0.0067
    maxFee = 0.02
elif tokenCorrelation > 0.7:
    print(f'Our correlation coefficient is {tokenCorrelation}. We are dealing with correlated assets')
    riskLevel = 2
    fee = 0.02
    minFee = 0.0137
    maxFee = 0.04
else:
    print(f'Our correlation coefficient is {tokenCorrelation}. We are dealing with weakly correlated assets')
    riskLevel = 3
    fee = 0.03
    minFee = 0.02
    maxFee = 0.06

print(f'Fee: {fee} \n Minimum Fee: {minFee} \n Maximum Fee: {maxFee}')

##################### parameter determination #####################
if riskLevel == 0:
    m = 0.009
    p = 8
    n = 1 
elif riskLevel == 1:
    m = 0.009
    p = 7.5
    n = 1 
elif riskLevel == 2:
    m = 0.007
    p = 7.5
    n = 1 
elif riskLevel == 3:
    m = 0.005
    p = 6
    n = 0.9

k= 1