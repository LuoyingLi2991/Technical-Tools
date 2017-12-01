# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 16:05:05 2017
 Filter for intra-day takeProfit systems. 
   The TP is the High/Low of the Previous Tradings using any intra-day
   trading frequency.

@author: luoying.li
"""

from TakeProfit import TakeProfit
import numpy as np
from Daily import Daily


class TakeProfit24hr(TakeProfit):
    def __init__(self,data,tradeSignal,hiloWindow):
        """Constructor"""
        TakeProfit.__init__(self,data,tradeSignal)
        self.hiloWindow=hiloWindow
        self.daily=Daily(data)
        self.CalcTakeProfitSeries()
    def CalcTakeProfitSeries(self):
        """This method now calcs the takeProfit Level from the previous day's Hi/Lo. """
        tradeNumber=0
        takeProfitHit=0
        self.takeProfitContainer=np.zeros((self.numTrades,3))
        self.takeProfitLevelSeries=np.nan*np.ones((self.height,2))
        self.x=self.data[self.data.columns[0]].tolist()
        self.takeProfitFilterFX=self.data[self.data.columns[0]].tolist()  # Filtered FX starts with Original FX Series
        self.takeProfitFilterSignal=[0]*self.height
        
        for i in range(1,self.height): 
            # Take Profit Not Yet Hit
            if takeProfitHit==0:
                # Neutral->Neutral
                if self.tradeSignal[i]==0 and self.tradeSignal[i-1]==0:
                    self.takeProfitFilterSignal[i]=0  # Stay Neutral
                # Neutral-> Trade
                elif self.tradeSignal[i-1]==0 and abs(self.tradeSignal[i])>0:
                    tradeNumber=tradeNumber+1  # NEW Trade Number
                    self.tradeEntryLevel=self.x[i]  # Entry Level
                    self.takeProfitLevelSeries[i,:]=self.CalcTakeProfitLevel(i,self.tradeSignal[i])  # set take profit 
                    self.takeProfitFilterSignal[i]=self.tradeSignal[i]  # filter signal
                # Trade -> Neutral
                elif abs(self.tradeSignal[i-1])>0 and self.tradeSignal[i]==0:
                    if self.tradeSignal[i-1]>0:
                        self.BookTrade(tradeNumber,max(self.takeProfitLevelSeries[i-1,:]),0) # Trade DID NOT HIT TAKE PROFIT
                    else:
                        self.BookTrade(tradeNumber, self.takeProfitLevelSeries[i-1,-1],0) # Trade DID NOT HIT TAKE PROFIT
                    self.tradeEntryLevel=0
                    self.takeProfitFilterSignal[i]=0
                # Trade -> Trade (Trade Continuation)
                elif self.tradeSignal[i]==self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0 and abs(self.tradeSignal[i-1])>0:
                    # -- CHECK IF long TRADE HITS TAKE PROFIT
                    if self.tradeSignal[i]==1 and self.x[i]<self.takeProfitLevelSeries[i-1,0]:
                        takeProfitHit=1  # TAKE PROFIT!!
                        self.BookTrade(tradeNumber,max(self.takeProfitLevelSeries[i-1,:]),1)  # Trade DID HIT TAKE PROFIT
                        self.takeProfitFilterSignal[i]=0
                        self.tradeEntryLevel=0
                        self.takeProfitFilterFX[i]=max(self.takeProfitLevelSeries[i-1,:])
                    # -- CHECK IF short TRADE HITS TAKE PROFIT    
                    elif self.tradeSignal[i]==-1 and self.x[i]>self.takeProfitLevelSeries[i-1,1]:  
                        takeProfitHit=1  # TAKE PROFIT!!
                        self.BookTrade(tradeNumber,self.takeProfitLevelSeries[i-1,-1],1)  # Trade DID HIT TAKE PROFIT
                        self.takeProfitFilterSignal[i]=0
                        self.tradeEntryLevel=0
                        self.takeProfitFilterFX[i]=self.takeProfitLevelSeries[i-1,-1]
                    # -- TRADE Does NOT HIT Take PROFIT 
                    else:
                        self.takeProfitLevelSeries[i,:]=self.CalcTakeProfitLevel(i,self.tradeSignal[i])  # Refresh Take Profit
                        self.takeProfitFilterSignal[i]=self.tradeSignal[i]
                # +Trade -> -Trade(Flip Trade)
                elif self.tradeSignal[i]!=self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0 and abs(self.tradeSignal[i-1])>0:
                    # -- CHECK IF long TRADE HITS TAKE PROFIT
                    if self.tradeSignal[i]==1 and self.x[i]<self.takeProfitLevelSeries[i-1,0]:
                        self.BookTrade(tradeNumber, max(self.takeProfitLevelSeries[i-1,:]),1) #  Trade DID HIT TAKE PROFIT
                        self.takeProfitFilterFX[i]=max(self.takeProfitLevelSeries[i-1,:])
                        tradeNumber=tradeNumber+1
                        self.tradeEntryLevel=max(self.takeProfitLevelSeries[i-1,:])
                    # -- CHECK IF short TRADE HITS TAKE PROFIT
                    elif self.tradeSignal[i]==-1 and self.x[i]>self.takeProfitLevelSeries[i-1,1]:
                        self.BookTrade(tradeNumber,self.takeProfitLevelSeries[i-1,-1],1)  #  Trade DID HIT TAKE PROFIT
                        self.takeProfitFilterFX[i] = self.takeProfitLevelSeries[i-1,-1]
                        tradeNumber=tradeNumber+1
                        self.tradeEntryLevel=self.takeProfitLevelSeries[i-1,-1]
                    # -- Trade Flipped WITHOUT TAKE PROFIT BEING HIT 
                    else:
                        self.BookTrade(tradeNumber,self.x[i],0) # Trade Not HIT TAKE PROFIT
                        self.takeProfitFilterFX[i]=self.x[i]
                        tradeNumber=tradeNumber+1  # NEW Trade Number
                        self.tradeEntryLevel=self.x[i]  # set NEW trade entry level
                    takeProfitHit=0
                    self.takeProfitLevelSeries[i,:]=self.CalcTakeProfitLevel(i,self.tradeSignal[i])
                    self.takeProfitFilterSignal[i]=self.tradeSignal[i]
            else: # Take Profit HIT
                # Trade -> Neutral
                if abs(self.tradeSignal[i-1])>0 and self.tradeSignal[i]==0:
                    takeProfitHit=0
                    self.tradeEntryLevel=0
                    self.takeProfitFilterSignal[i]=0
                # Trade -> Trade (Trade Continuation)
                elif self.tradeSignal[i]==self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0 and abs(self.tradeSignal[i-1])>0:
                    takeProfitHit=1
                    self.takeProfitFilterSignal[i]=0
                    self.tradeEntryLevel=0
                # +Trade -> -Trade(Flip Trade)
                elif self.tradeSignal[i]!=self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0 and abs(self.tradeSignal[i-1])>0:
                    takeProfitHit=0
                    tradeNumber=tradeNumber+1
                    self.tradeEntryLevel=self.x[i]
                    self.takeProfitLevelSeries[i,:]=self.CalcTakeProfitLevel(i,self.tradeSignal[i])
                    self.takeProfitFilterSignal[i]=self.tradeSignal[i]
    
    def CalcTakeProfitLevel(self,todayIndex,tradeSignal):
        if self.hiloWindow=='yesterday':
            hiLoPrices =self.daily.findYesterdayHiLo(todayIndex)  # Get Yesterday's hi/lo price
        else:
            hiLoPrices =self.daily.find24hrHiLo(todayIndex)  # Get 24hr hi/lo price
        if tradeSignal==1:
            level=hiLoPrices[0]
            tpLevel=[level,np.nan]
        else:
            level=hiLoPrices[1]
            tpLevel=[np.nan,level]
        return tpLevel
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                    