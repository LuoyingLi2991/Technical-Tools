# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 14:03:15 2017
Dummy StopLoss Object that does not filter the trade signal with stops@author: luoying.li
"""

from StopLoss import StopLoss
from MovingAverage import MovingAverage
import pandas as pd



class StopLossDummy(StopLoss):
    def __init__(self,data,tradeSignal):
        """Constructor"""
        StopLoss.__init__(self,data,tradeSignal)
        self.stopFilteredSignal=self.tradeSignal
        self.stopFilteredFX=self.data[self.data.columns[0]].tolist()
    def FilterFXSeries(self):
        """Implementation of abstract class"""
        filtFX=self.data[self.data.columns[0]].tolist()
        return filtFX
    def CalcStopLevel(self,entryLevel,tradeSignal):
        """Dummy implementation for Abstraction"""
        pass
    


"""  
if __name__ == "__main__":
    data=pd.read_excel("c:\Book1.xlsx")
    data.set_index("Date",inplace=True)
    ma=MovingAverage(data,'EMA',5)
    tS=ma.TradeSignal
    s=StopLossDummy(data,tS)
    print s.stopLossSeries
"""