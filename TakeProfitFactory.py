# -*- coding: utf-8 -*-
"""
Created on Fri Dec 08 11:11:27 2017

@author: luoying.li
"""
from TakeProfitDummy import TakeProfitDummy
from TakeProfitFixed import TakeProfitFixed
from TakeProfit24hr import TakeProfit24hr
from TakeProfitEquity import TakeProfitEquity


class TakeProfitFactory:
    @staticmethod
    def getInstance(Type,data,tradeSignal,*takeProfitRules):
        if Type=='Dummy':
            obj=TakeProfitDummy(data,tradeSignal)
        elif Type=='Fixed':
            obj=TakeProfitFixed(data,tradeSignal,takeProfitRules[0])
        elif Type=='PnL':
            obj=TakeProfitEquity(data,tradeSignal,takeProfitRules[0],takeProfitRules[1])
        return obj