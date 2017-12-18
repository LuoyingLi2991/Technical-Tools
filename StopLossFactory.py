# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 14:08:11 2017

@author: luoying.li
"""
from StopLossFixed import StopLossFixed
from StopLossDummy import StopLossDummy
from StopLossTimeCutOff import StopLossTimeCutOff
import pandas as pd
from MovingAverage import MovingAverage


class StopLossFactory:
    
    @staticmethod
    def getInstance(Type,data,tradeSignal,*stop):
        if Type=='Dummy':
            obj=StopLossDummy(data,tradeSignal)
        elif Type=='Fixed':
            obj=StopLossFixed(data,tradeSignal,stop[0])
        elif Type=='TimeCutOff':
            obj=StopLossTimeCutOff(data,tradeSignal,stop[0])
        return obj
        
