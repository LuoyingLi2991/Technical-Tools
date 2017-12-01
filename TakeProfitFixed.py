# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 15:30:48 2017
Filter for takeProfit that is a fixed percentage from the highs
@author: luoying.li
"""

from TakeProfit import TakeProfit
import numpy as np
from MovingAverage import MovingAverage
import pandas as pd


class TakeProfitFixed(TakeProfit):
    def __init__(self,data,tradeSignal,takeProfitRule):
        """Constructor"""
        TakeProfit.__init__(self,data,tradeSignal)
        self.takeProfitRule=takeProfitRule
        self.CalcTakeProfitSeries()
        
    def CalcTakeProfitLevel(self,highWaterMark, tradeSignal):
        if tradeSignal==1:
            level=highWaterMark*(1-(self.takeProfitRule+0.0)/100)  # Set the NEW take profit BELOW the market 
            tpLevel=[level,np.nan]
        else:
            level=highWaterMark*(1+(self.takeProfitRule+0.0)/100)  # Set the OLD take profit ABOVE the market
            tpLevel=[np.nan,level]
        return tpLevel


if __name__ == "__main__":
    data=pd.DataFrame([1.0455,1.0405,1.0489,1.0607,1.0532,1.0574,1.0554,1.0582,
                       1.0613,1.0643,1.0601,1.0713,1.063,1.0664,1.0703,1.0765,
                       1.0731,1.0748,1.0682,1.0699,1.0695,1.0798,1.0769,1.0759,
                       1.0783,1.075,1.0683,1.0698,1.0655,1.0643])
    MAWindow=5
    ma=MovingAverage(data,'EMA',5)
    tradeSignal=ma.TradeSignal
    t=TakeProfitFixed(data,tradeSignal,5)
    print t.takeProfitContainer
    