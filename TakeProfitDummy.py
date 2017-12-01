# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 15:50:59 2017

@author: luoying.li
"""
from TakeProfit import TakeProfit



class TakeProfitDummy(TakeProfit):
    def __init__(self,data,tradeSignal):
        TakeProfit.__init__(self,data,tradeSignal)
        self.takeProfitFilterSignal=self.tradeSignal
        self.takeProfitFilterFX=self.data[self.data.columns[0]].tolist()
    def CalcTakeProfitLevel(self,highWaterMark,tradeSignal):
        pass
    
    