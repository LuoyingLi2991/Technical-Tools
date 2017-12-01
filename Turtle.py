# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 14:12:25 2017
The Classic Turtle Model - breakouts occur if day hi or lo breaches.
    Likewise for stops.
    
    range
    
    METHODS
    =======
    CalcRanges() - calcs the Hi/Lo for the BreakOut and BreakIn Ranges.
                   USES Static Class LookBackWindow to determine ranges from [Close,Open,Hign, Low]
    CalcTradeSignal() - calc Turtle Trade Signal
    CalcRangeLocation() - calc the location in the range
    CalcBreakoutLocation() - calc location between maxPnL and breakout
                              level [0,1]. N.b., that if fall back into range, then -> [0] reading
                             [+/-] represents long or short trades. 
    CalcTodayData() - Calcs Today's signal trade Signal, trade Days, range
                      days and range Location.
    CalcZscore() - Calc today's Z-Scores for tradeDays and rangeDays 
    CalcMax() - Calc the new Max Trade PnL (STATIC)
    
    

@author: luoying.li
"""
import sys
sys.path.append('P:\Python Library') 

import pandas as pd
from LookBackWindow import LookBackWindow
import numpy as np
from UtilityClass import UtilityClass


class Turtle():
    def __init__(self,data,outWindow,inWindow,*assetType):
        if 'PX_LAST' in data.columns:
            data.rename(columns={'PX_LAST':'Close'},inplace=True)
        else:
            oldName=data.columns[0]
            data.rename(columns={oldName:'Close'},inplace=True)
        if len(data.columns)==1:  # Check if x is just 'Close'
            data['Open']=data['Close']
            data['High']=data['Close']
            data['Low']=data['Close']
        self.data=data.fillna(method='bfill', axis=1)  # Pre-Clean Data for NaN
        if assetType!=():  # optional parameter
            self.assetType='bond'
        else:
            self.assetType=None
        self.innerWindow=inWindow
        self.outerWindow=outWindow
        self.CalcRanges()
        self.CalcTradeSignal()
        self.CalcBreakoutLocation()
        self.CalcTodayData()
        self.CalcZscores()
    
    def CalcRanges(self):
        """calcs the Hi/Lo for the BreakOut and BreakIn Ranges"""
        lbw=LookBackWindow()
        self.breakOutRange=lbw.CalcHiLoSeries(self.data,self.outerWindow)
        self.breakInRange=lbw.CalcHiLoSeries(self.data,self.innerWindow)
    
    def CalcTradeSignal(self):
        """calc Turtle Trade Signal"""
        self.entryLevel=0
        maxTradePnL=0
        self.tradeSignal=list(np.zeros(len(self.data)))
        self.tradeDays=list(np.zeros(len(self.data)))
        self.rangeDays=list(np.zeros(len(self.data)))
        self.rangeLocation=list(np.zeros(len(self.data)))
        self.pctMoveFromBreakOut=list(np.zeros(len(self.data)))
        self.maxMoveFromBreakOut=list(np.zeros(len(self.data)))
        
        for i in range(self.outerWindow,len(self.data)):  
            if self.tradeSignal[i-1]==0:  # Neutral
                if self.data['High'].iloc[i]>self.breakOutRange['RollMax'].iloc[i]:  # If above the 20d high 
                    self.tradeSignal[i]=1  # Go Long
                    self.tradeDays[i]=self.tradeDays[i-1]+1
                    self.entryLevel=self.breakOutRange['RollMax'].iloc[i]  # entry level at the break
                elif self.data['Low'].iloc[i]<self.breakOutRange['RollMin'].iloc[i]:  # If below the 20d low
                    self.tradeSignal[i]=-1 # Go Short
                    self.tradeDays[i]=self.tradeDays[i-1]-1
                    self.entryLevel=self.breakOutRange['RollMin'].iloc[i]  # entry level at the break
                else:
                    self.rangeDays[i]=self.rangeDays[i-1]+1  # Another day in the range
                    self.rangeLocation[i]=self.CalcRangeLocation(i)
            elif self.tradeSignal[i-1]==1:  # Long
                if self.data['Low'].iloc[i]<self.breakInRange['RollMin'].iloc[i]:  # If day low below the 10d lo
                    self.tradeSignal[i]=0  # Go Back to Neutral on BreakIn
                    self.rangeDays[i] = 1;  # start rangeDay Count
                    self.rangeLocation[i] = self.CalcRangeLocation(i) 
                    self.entryLevel=0
                    maxTradePnL=0
                else:
                    self.tradeSignal[i]=1  # Stay Long
                    self.tradeDays[i]=self.tradeDays[i-1]+1
                    self.pctMoveFromBreakOut[i]=self.CalcPctMoveFromBreakOut(self.data['Close'].iloc[i],self.entryLevel,1)
                    maxTradePnL=Turtle.CalcMax(maxTradePnL, self.pctMoveFromBreakOut[i])
                    self.maxMoveFromBreakOut[i]=maxTradePnL
            elif self.tradeSignal[i-1]==-1:  # Short
                if self.data['High'].iloc[i]>self.breakInRange['RollMax'].iloc[i]:  # if day hi above the 10d high
                    self.tradeSignal[i]=0  # Go Back To Neutral on BreakIn
                    self.tradeDays[i]=0
                    self.rangeDays[i]=1  # start rangeDay Count
                    self.rangeLocation[i]=self.CalcRangeLocation(i)
                    self.entryLevel=0
                    maxTradePnL=0
                else:
                    self.tradeSignal[i]=-1  # stay short
                    self.tradeDays[i]=self.tradeDays[i-1]-1
                    self.pctMoveFromBreakOut[i]=self.CalcPctMoveFromBreakOut(self.data['Close'].iloc[i],self.entryLevel,-1)
                    maxTradePnL=Turtle.CalcMax(maxTradePnL,self.pctMoveFromBreakOut[i])
                    self.maxMoveFromBreakOut[i]=maxTradePnL
    
    def CalcRangeLocation(self,i):
        """calc the location in the range"""
        if self.tradeSignal[i]==0:
            Range=self.breakOutRange['RollMax'].iloc[i]-self.breakOutRange['RollMin'].iloc[i]
            r=(self.data['Close'].iloc[i]-self.breakOutRange['RollMin'].iloc[i]+0.0)/Range
        return r
    def CalcPctMoveFromBreakOut(self,spot,entry,shortOrLong):
        """calc location between maxPnL and breakout"""
        if shortOrLong==1:
            if self.assetType=='bond':  # if Long and a Bond
                pct=spot-entry
            else:
                pct=(spot/entry-1)*100
        else:
            if self.assetType=="bond":
                pct = -(spot - entry)  # if Short and a bond
            else:
                pct = -((spot+0.0)/entry-1)*100;
        return pct
    def CalcBreakoutLocation(self):
        """Gives location range [0,1] for all winning trades. Note that -/+ represents long or short trades."""
        self.breakoutLocation=list(np.zeros(len(self.pctMoveFromBreakOut)))
        for i in range(len(self.pctMoveFromBreakOut)):
            if self.maxMoveFromBreakOut[i]!=0 and self.pctMoveFromBreakOut[i]>0:
                self.breakoutLocation[i]=((self.pctMoveFromBreakOut[i]+0.0)/self.maxMoveFromBreakOut[i])*self.tradeSignal[i]
    def CalcTodayData(self):
        self.tradeSignalToday=self.tradeSignal[-1]
        self.tradeDaysToday = self.tradeDays[-1]
        self.rangeDaysToday = self.rangeDays[-1]
        self.rangeLocationToday = self.rangeLocation[-1]
        self.pctMoveFromBreakOutToday =self.pctMoveFromBreakOut[-1]
        self.maxMoveFromBreakoutToday = self.maxMoveFromBreakOut[-1]
        self.breakoutLocationToday = self.breakoutLocation[-1]
    
    def CalcZscores(self):
        u=UtilityClass()
        if self.tradeDaysToday!=0:
            td=np.array(self.tradeDays)
            filterTradeZeros=list(td[td!=0])  # Exclude RangeDays (0)
            df=pd.DataFrame(filterTradeZeros)
            self.tradeDaysToday_Zscore=u.calc_z_score(df,False)[1]
        else:
            self.tradeDaysToday_Zscore=0
        
        if self.rangeDaysToday!=0:
            td=np.array(self.rangeDays)
            filterRangeZeros=list(td[td!=0])  # Exclude TradeDays 
            df=pd.DataFrame(filterRangeZeros)
            self.rangeDaysToday_Zscore=u.calc_z_score(df,True)[1]  # Symmetric Z-Score
        else:
            self.rangeDaysToday_Zscore=0
            
        if self.pctMoveFromBreakOutToday!=0:
            td=np.array(self.pctMoveFromBreakOut)
            filterPctMove=list(td[td!=0])
            df=pd.DataFrame(filterPctMove)
            self.pctMove_Zscore=u.calc_z_score(df,False)[1]
        else:
            self.pctMove_Zscore=0
    
    @staticmethod
    def CalcMax(Max,pnl):
        if pnl>Max:
            m=pnl
        else:
            m=Max
        return m
    


                    



"""

if __name__ == "__main__":
    data=pd.read_excel("c:\Book1.xlsx")
    data.set_index("Date",inplace=True)
    t=Turtle(data,3,5)
    
"""    