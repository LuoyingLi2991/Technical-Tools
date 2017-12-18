# -*- coding: utf-8 -*-
"""
Created on Fri Dec 08 11:21:00 2017

@author: luoying.li
"""

from TakeProfit import TakeProfit
import numpy as np


class TakeProfitEquity(TakeProfit):
    def __init__(self,data,tradeSignal,takeProfitRule,takeProfitPnLRule):
        TakeProfit.__init__(self,data,tradeSignal)
        self.takeProfitRule=takeProfitRule
        self.takeProfitPnLRule=takeProfitPnLRule
        self.CalcTakeProfitSeries()
        
    def CalcTakeProfitLevel(self,highWaterMark,tradeSignal):
        maxPnL=self.CalcMaxTradePnL(tradeSignal,highWaterMark)
        lossPnL=maxPnL*self.takeProfitPnLRule/100
        
        if tradeSignal==1:
            level=highWaterMark*(1-self.takeProfitPnLRule/100)
            level=level-lossPnL
            tpLevel=[level,np.nan]
        else:
            level=highWaterMark*(1+self.takeProfitPnLRule/100)
            level=level+lossPnL
            tpLevel=[np.nan,level]
        return tpLevel