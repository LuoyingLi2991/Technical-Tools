# -*- coding: utf-8 -*-
"""
Created on Tue Dec 05 09:14:16 2017
      Determines the FX Sharpe Ratio. 
      Usual Input is the Daily Returns, But Can Deal with Cumulative
      Returns if flagged with third parameter = 'cumulRet' 

@author: luoying.li
"""
import numpy as np
from math import sqrt


class SharpeRatio:
    def __init__(self,returnSeries,dataFreq,*cumulRet):
        """Constructor"""
        if cumulRet==():  # Check if Normal Returns or Cumulative Returns
            self.x=returnSeries
        elif cumulRet[0]=='cumulRet':  # check for Flag indicating Cumulative Returns have been passed to the data
            self.x=self.ConvertReturnSeries(returnSeries)
        else:
            raise("Incorrect Input")
        self.dataFreq=dataFreq
        self.sharpeRatio=self.CalcSharpe()
    
    def CalcSharpe(self):
        """Calc Sharpe Ratio"""
        self.scaling=self.DetermineScaling(self.dataFreq)
        self.avg=np.nanmean(self.x)
        self.vol=np.nanstd(self.x)
        s=(self.avg/self.vol)*self.scaling
        return s
    
    @staticmethod
    def DetermineScaling(dataFreq):
        """Determine Conversion Scaling for different data frequency"""
        if dataFreq=='daily':
            s=252/sqrt(252)
        elif dataFreq=='weekly':
            s=52/sqrt(52)
        elif dataFreq=='monthly':
            s=12/sqrt(12)
        elif dataFreq=='quarterly':
            s=4/sqrt(4)
        elif dataFreq=='annual':
            s=1
        return s
    
    @staticmethod
    def ConvertReturnSeries(cumulRet):
        """Convert from Cumulative Return"""
        fwdShift=np.roll(cumulRet,1,axis=0)
        convert = (cumulRet+0.0)/fwdShift-1
        convert = convert[1:]
        return convert
        
    
            
        
    