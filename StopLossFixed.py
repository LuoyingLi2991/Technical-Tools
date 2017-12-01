# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 11:59:59 2017
  SubClass of StopLoss, where the stop rule is a fixed percentage away
  from the entry point.

@author: luoying.li
"""

from StopLoss import StopLoss
from MovingAverage import MovingAverage
import pandas as pd
import numpy as np


class StopLossFixed(StopLoss):
    # Constructor  
    def __init__(self, data, tradeSignal, stop):
        StopLoss.__init__(self,data,tradeSignal)
        self.stop=stop
        self.stopFilteredSignal=self.RunStopLoss()
        self.stopRatio=self.CalcStopRatio()
    # Set Stop Level
    def CalcStopLevel(self,entryLevel, tradeSignal):
        sLevel=[]
        if tradeSignal==1: # Long
            Level=entryLevel*(1-(self.stop+0.0)/100)  # Long Trade (Stop below Entry)
            sLevel=[Level,np.NaN]
        else: # SHORT
            Level=entryLevel*(1+(self.stop+0.0)/100)  # Set the stop ABOVE the market
            sLevel=[np.NaN,Level]
        return sLevel
    
    
    
if __name__ == "__main__":
    data=pd.read_excel("c:\Book1.xlsx")
    data.set_index("Date",inplace=True)
    ma=MovingAverage(data,'EMA',5)
    tS=ma.TradeSignal
    s=StopLossFixed(data,tS,10)
    print s.CalcStopLevel(1.0613,1)
    