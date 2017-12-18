# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 09:57:26 2017
% Calculates DrawDown for 1 or more series of cumulative returns
@author: luoying.li
"""
import numpy as np

class DrawDown:
    def __init__(self,cumulReturns):
        """Constructor"""
        self.cumulReturns=cumulReturns
        self.height=self.cumulReturns.shape[0]
        if len(self.cumulReturns.shape)>1:
            self.width=self.cumulReturns.shape[1]
        else:
            self.width=1
        self.drawDownSeries=self.CalcDrawDown()
        self.maxDrawDown=self.CalcMaxDrawDown()
        
    def CalcDrawDown(self):
        """DD on  accumulateModelReturns"""
        dd=np.zeros((self.height,self.width))
        if self.width>1:
            for i in range(self.width):
                StartLoop=[k for k,r in enumerate(self.cumulReturns[:,i]) if r>1][0]+1  # find the first +ve trade
                high=self.cumulReturns[StartLoop,i]   # remembers the last high
                
                for j in range(StartLoop,self.height):
                    if self.cumulReturns[j,i]-high>=0:
                        dd[j,i]=0
                        high=self.cumulReturns[j,i]
                    else:
                        dd[j,i]=((self.cumulReturns[j,i]+0.0)/high-1)
        else:
            StartLoop=[k for k,r in enumerate(self.cumulReturns) if r>1][0]+1  # find the first +ve trade
            high=self.cumulReturns[StartLoop]   # remembers the last high
            
            for j in range(StartLoop,self.height):
                if self.cumulReturns[j]-high>=0:
                    dd[j,0]=0
                    high=self.cumulReturns[j]
                else:
                    dd[j,0]=((self.cumulReturns[j]+0.0)/high-1)
        return dd
    
    def CalcMaxDrawDown(self):
        if self.width>1:
            maxDD=self.drawDownSeries.min(axis=0)
        else:
            maxDD=min(self.drawDownSeries)
        return maxDD
    
            