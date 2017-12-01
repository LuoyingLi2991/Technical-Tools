# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 14:15:38 2017
    SubClass of StopLoss, where the stop rule is based on a TIME limit
    following entry.
    If Long: stop hit when x < entry at i=i+timeStop  
    If Short stop hit when x > entry at i=i+timeStop

@author: luoying.li
"""

from StopLoss import StopLoss
import numpy as np
import pandas as pd
from MovingAverage import MovingAverage



class StopLossTimeCutOff(StopLoss):
    def __init__(self,data,tradeSignal,timeStop):
        """Constructor"""
        StopLoss.__init__(self,data,tradeSignal)
        self.timeStop=timeStop
        self.stopFilteredSignal=self.RunStopLoss()
        self.stopRatio=self.CalcStopRatio()
        
    def RunStopLoss(self):
        slFilter=[0]*self.height
        self.stopLossSeries=np.nan*np.ones((self.height+self.timeStop,2))
        self.stopFilteredFX=self.data[self.data.columns[0]].tolist()  # Filtered FX starts with Original FX Series
        hitStopFlag=0  # Flag +1 if hit trade in the stop  
        self.stopContainer=np.zeros((self.numTrades,3))
        tradeNumber=0
        for i in range(1,self.height):
            #  STOP NOT HIT
            if hitStopFlag==0:
                #  Neutral ->  Trade
                if self.tradeSignal[i-1]==0 and abs(self.tradeSignal[i])>0:
                    tradeNumber=tradeNumber+1  # New Trade
                    hitStopFlag=0
                    self.stopLossSeries[i+self.timeStop,:]=self.CalcStopLevel(self.data[self.data.columns[0]].iloc[i],self.tradeSignal[i])
                    slFilter[i]=self.tradeSignal[i]
                #  Trade -> Neutral
                elif abs(self.tradeSignal[i-1])>0 and self.tradeSignal[i]==0:
                    self.BookTrade(tradeNumber,self.data[self.data.columns[0]].iloc[i],0)
                    hitStopFlag=0
                    slFilter[i]=0
                #  Old Trade -> New Trade
                elif self.tradeSignal[i]!=self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0 and abs(self.tradeSignal[i-1])>0:
                    #  CHECK FIRST IF long TRADE HITS STOP BEFORE FLIP
                    if self.tradeSignal[i-1]==1 and self.data[self.data.columns[0]].iloc[i]<self.stopLossSeries[i,0] and not np.isnan(self.stopLossSeries[i,0]):
                        self.BookTrade(tradeNumber,self.data[self.data.columns[0]].iloc[i],1)
                        self.stopFilteredFX[i]=self.data[self.data.columns[0]].iloc[i] 
                    #  CHECK FIRST IF short TRADE HITS STOP BEFORE FLIP
                    elif self.tradeSignal[i-1]==-1 and self.data[self.data.columns[0]].iloc[i]>self.stopLossSeries[i,1] and not np.isnan(self.stopLossSeries[i,1]):
                        self.BookTrade(tradeNumber,self.data[self.data.columns[0]].iloc[i],1)
                        self.stopFilteredFX[i]=self.data[self.data.columns[0]].iloc[i]
                    #  Trade Flipped WITHOUT STOP BEING HIT    
                    else:
                        self.BookTrade(tradeNumber,self.data[self.data.columns[0]].iloc[i],0)
                    tradeNumber=tradeNumber+1
                    hitStopFlag=0
                    self.stopLossSeries[i+self.timeStop,:]=self.CalcStopLevel(self.data[self.data.columns[0]].iloc[i],self.tradeSignal[i])
                    slFilter[i]=self.tradeSignal[i]
                #  Trade -> Trade    
                elif self.tradeSignal[i]==self.tradeSignal[i-1] and self.tradeSignal[i]!=0:
                    #  CHECK IF long TRADE HITS STOP
                    if self.tradeSignal[i]==1 and self.data[self.data.columns[0]].iloc[i]<self.stopLossSeries[i,0] and not np.isnan(self.stopLossSeries[i,0]):
                        hitStopFlag=1
                        self.BookTrade(tradeNumber,self.data[self.data.columns[0]].iloc[i],1)
                        self.stopFilteredFX[i]=self.data[self.data.columns[0]].iloc[i]
                        slFilter[i]=0
                    #  CHECK IF short TRADE HITS STOP
                    elif self.tradeSignal[i]==-1 and self.data[self.data.columns[0]].iloc[i]>self.stopLossSeries[i,1] and not np.isnan(self.stopLossSeries[i,1]):
                        hitStopFlag=1
                        self.BookTrade(tradeNumber,self.data[self.data.columns[0]].iloc[i],1)
                        self.stopFilteredFX[i]=self.data[self.data.columns[0]].iloc[i]
                        slFilter[i]=0
                    #  NO Stop Hit, Continue Trade
                    else:
                        hitStopFlag = 0
                        slFilter[i] = self.tradeSignal[i]
            else:  # STOP HIT    
                #  Trade -> Trade = Suppress Signal 
                if self.tradeSignal[i]==self.tradeSignal[i-1]:
                    hitStopFlag=1
                    slFilter[i]=0
                #  Old Trade -> New Trade = End Signal Suppression
                elif self.tradeSignal[i]!=self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0:
                    tradeNumber=tradeNumber+1
                    hitStopFlag=0
                    self.stopLossSeries[i+self.timeStop,:]=self.CalcStopLevel(self.data[self.data.columns[0]].iloc[i],self.tradeSignal[i])
                    slFilter[i]=self.tradeSignal[i]
        #  Add last trade in series if it is still live
        if self.stopContainer[-1,0]==0:
            self.BookTrade(tradeNumber,self.data[self.data.columns[0]].iloc[i],0)
        self.stopLossSeries=self.stopLossSeries[: -self.timeStop,:]
        return slFilter
    def CalcStopLevel(self,entryLevel,tradeSignal):
        """Set Stop Level"""
        if tradeSignal==1:  # Long
            Level=entryLevel 
            sLevel=[Level,np.NaN]
        else: # Short
            Level=entryLevel
            sLevel=[np.NaN,Level]
        return sLevel
    
       
"""                
if __name__ == "__main__":
    data=pd.read_excel("c:\Book1.xlsx")
    data.set_index("Date",inplace=True)
    ma=MovingAverage(data,'EMA',5)
    tS=ma.TradeSignal
    s=StopLossTimeCutOff(data,tS,1)                
"""                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                