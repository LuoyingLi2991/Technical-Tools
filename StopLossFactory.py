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
        elif Type=='Time':
            obj=StopLossTimeCutOff(data,tradeSignal,stop[0])
        return obj
        
if __name__ == "__main__":
    s=StopLossFactory()
    data=pd.DataFrame([1.0455,1.0405,1.0489,1.0607,1.0532,1.0574,1.0554,1.0582,
                       1.0613,1.0643,1.0601,1.0713,1.063,1.0664,1.0703,1.0765,
                       1.0731,1.0748,1.0682,1.0699,1.0695,1.0798,1.0769,1.0759,
                       1.0783,1.075,1.0683,1.0698,1.0655,1.0643])
    MAWindow=5
    ma=MovingAverage(data,'EMA',5)
    tradeSignal=ma.TradeSignal
    a=s.getInstance('Fixed',data,tradeSignal,5)
    print a.stopLossSeries