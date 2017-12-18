# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 10:57:29 2017
Abstract SuperClass of TakeProfit Objects
    
     Methods
     -------
     CalcTakeProfitSeries() - Calcs the takeProfitFilter Signal and FX
     BookTrade() - Helps book the takeProfit data in the tradeContainer
     CountTrades() - Count the number of trades
     CalcTakeProfitLevel() - ABSTRACT - calc the takeProfit Level
     CalcHighWaterMark() - STATIC - determine the price high to make the
                           takeprofitlevel from
     CalcMaxTradePnL() - calc the Max PnL of a trade from highWaterMark 

@author: luoying.li
"""

import abc
import numpy as np



class TakeProfit:
    __metaclass__ = abc.ABCMeta
    def __init__(self,data,tradeSignal):
        self.data=data
        self.x=data[data.columns[0]].tolist()
        self.dates=data.index.tolist()
        self.height=len(self.data)
        self.tradeSignal=tradeSignal
        self.numTrades=self.CountTrades()
    def CalcTakeProfitSeries(self):
        tradeNumber=0
        takeProfitHit=0
        highWaterMark=0
        self.takeProfitContainer=np.zeros((self.numTrades,3))
        self.takeProfitLevelSeries=np.nan*np.ones((self.height,2))
        self.takeProfitFilterFX=self.data[self.data.columns[0]].tolist()
        self.takeProfitFilterSignal=[0]*self.height

        for i in range(1,self.height):
            # Take Profit Not Yet Hit
            if takeProfitHit==0:
                # Neutral->Neutral
                if self.tradeSignal[i]==0 and self.tradeSignal[i-1]==0:
                    self.takeProfitFilterSignal[i]=0
                # Neutral-> Trade
                elif self.tradeSignal[i-1]==0 and abs(self.tradeSignal[i])>0:
                    tradeNumber=tradeNumber+1  # New Trade Number
                    self.tradeEntryLevel=self.data[self.data.columns[0]].iloc[i]  # Entry Level
                    highWaterMark=self.data[self.data.columns[0]].iloc[i]  # set highwatermark at spot entry
                    self.takeProfitLevelSeries[i,:]=self.CalcTakeProfitLevel(highWaterMark,self.tradeSignal[i])  # set take profit 
                    self.takeProfitFilterSignal[i]=self.tradeSignal[i]  # filter signal
                # Trade -> Neutral
                elif abs(self.tradeSignal[i-1])>0 and self.tradeSignal[i]==0: 
                    if self.tradeSignal[i]==1:
                        self.BookTrade(tradeNumber,max(self.takeProfitLevelSeries[i-1,:]),0)  # Trade DID NOT HIT TAKE PROFIT
                    else:
                        self.BookTrade(tradeNumber,self.takeProfitLevelSeries[i-1,-1],0)
                    self.tradeEntryLevel=0
                    highWaterMark=0
                    self.takeProfitFilterSignal[i]=0
                # Trade -> Trade (Trade Continuation)
                elif self.tradeSignal[i]==self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0 and abs(self.tradeSignal[i-1])>0:
                    # -- CHECK IF long TRADE HITS TAKE PROFIT
                    if self.tradeSignal[i]==1 and self.data[self.data.columns[0]].iloc[i]<self.takeProfitLevelSeries[i-1,0]:
                        takeProfitHit=1
                        self.BookTrade(tradeNumber,max(self.takeProfitLevelSeries[i-1,:]),1)
                        self.takeProfitFilterSignal[i]=0
                        self.tradeEntryLevel = 0
                        highWaterMark = 0
                        self.takeProfitFilterFX[i] =max(self.takeProfitLevelSeries[i-1,:])
                    # -- CHECK IF short TRADE HITS TAKE PROFIT
                    elif self.tradeSignal[i]==-1 and self.data[self.data.columns[0]].iloc[i]>self.takeProfitLevelSeries[i-1,1]:
                        takeProfitHit=1
                        self.BookTrade(tradeNumber, self.takeProfitLevelSeries[i-1,-1],1)
                        self.takeProfitFilterSignal[i]=0
                        self.tradeEntryLevel = 0
                        highWaterMark = 0
                        self.takeProfitFilterFX[i] =max(self.takeProfitLevelSeries[i-1,:])
                    # TRADE Does NOT HIT Take PROFIT 
                    else:
                        highWaterMark=self.CalcHighWaterMark(self.data[self.data.columns[0]].iloc[i],self.tradeSignal[i],highWaterMark)
                        self.takeProfitLevelSeries[i,:]=self.CalcTakeProfitLevel(highWaterMark,self.tradeSignal[i])
                        self.takeProfitFilterSignal[i]=self.tradeSignal[i]
                #  +Trade -> -Trade(Flip Trade)
                elif self.tradeSignal[i]!=self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0 and abs(self.tradeSignal[i-1])>0:
                    # -- CHECK IF long TRADE HITS TAKE PROFIT
                    if self.tradeSignal[i]==1 and self.data[self.data.columns[0]].iloc[i]<self.takeProfitLevelSeries[i-1,0]:
                        self.BookTrade(tradeNumber,max(self.takeProfitLevelSeries[i-1,:]),1)
                        self.takeProfitFilterFX[i]=max(self.takeProfitLevelSeries[i-1,:])
                        tradeNumber=tradeNumber+1
                        self.tradeEntryLevel=max(self.takeProfitLevelSeries[i-1,:])
                        highWaterMark=self.tradeEntryLevel
                    # -- CHECK IF short TRADE HITS TAKE PROFIT
                    elif self.tradeSignal[i]==-1 and self.data[self.data.columns[0]].iloc[i]>self.takeProfitLevelSeries[i-1,1]:
                        self.BookTrade(tradeNumber,self.takeProfitLevelSeries[i-1,-1],1)
                        self.takeProfitFilterFX[i]=self.takeProfitLevelSeries[i-1,-1]
                        tradeNumber=tradeNumber+1
                        self.tradeEntryLevel=self.takeProfitLevelSeries[i-1,-1]
                        highWaterMark=self.tradeEntryLevel
                    # -- Trade Flipped WITHOUT TAKE PROFIT BEING HIT 
                    else:
                        self.BookTrade(tradeNumber,self.data[self.data.columns[0]].iloc[i],0)
                        self.takeProfitFilterFX[i]=self.data[self.data.columns[0]].iloc[i]
                        tradeNumber=tradeNumber+1
                        self.tradeEntryLevel=self.data[self.data.columns[0]].iloc[i]
                        highWaterMark=self.tradeEntryLevel
                    takeProfitHit = 0
                    self.takeProfitLevelSeries[i,:]=self.CalcTakeProfitLevel(highWaterMark, self.tradeSignal[i])
                    self.takeProfitFilterSignal[i]=self.tradeSignal[i]
            # Take Profit HIT
            else:
                # Trade -> Neutral
                if abs(self.tradeSignal[i-1])>0 and self.tradeSignal[i]==0:
                    takeProfitHit = 0
                    self.tradeEntryLevel=0
                    highWaterMark=0
                    self.takeProfitFilterSignal[i]=0
                # Trade -> Trade (Trade Continuation)
                elif self.tradeSignal[i]==self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0 and abs(self.tradeSignal[i-1])>0:
                    takeProfitHit = 1  # MAINTAIN FLAG
                    self.takeProfitFilterSignal[i]=0  # Maintain the FLAT SIGNAL
                    self.tradeEntryLevel=0
                    highWaterMark=0
                # +Trade -> -Trade(Flip Trade)
                elif self.tradeSignal[i]!= self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0 and abs(self.tradeSignal[i-1])>0:
                    takeProfitHit = 0  # RESET FLAG
                    tradeNumber = tradeNumber + 1 # NEW Trade Number
                    self.tradeEntryLevel=self.data[self.data.columns[0]].iloc[i] # set NEW entry
                    highWaterMark=self.data[self.data.columns[0]].iloc[i] # set highwatermark at spot entry
                    self.takeProfitLevelSeries[i,:]=self.CalcTakeProfitLevel(highWaterMark, self.tradeSignal[i])
                    self.takeProfitFilterSignal[i]=self.tradeSignal[i]
        
    def BookTrade(self,trNumber,takeProfitLevel,hit):
         """bookTrade - Helps book the takeProfit data in the tradeContainer"""
         self.takeProfitContainer[trNumber-1,0]=trNumber
         self.takeProfitContainer[trNumber-1,1]=takeProfitLevel
         self.takeProfitContainer[trNumber-1,2]=hit  # 1: if Stop Hit, or 0: if due to change in trade signal
    
    
    def CountTrades(self):
        """Count Num of Trades"""
        count=0
        for i in range(1,self.height):
            if self.tradeSignal[i]!=self.tradeSignal[i-1]:
                count=count+1
        return count
    
    def CalcMaxTradePnL(self,tradeSignal,highWaterMark):
        """calcMaxTradePnL"""
        if tradeSignal==1:
            pnl=highWaterMark-self.tradeEntryLevel
        else:
            pnl=self.tradeEntryLevel-highWaterMark
        return pnl
    
    @staticmethod
    def CalcHighWaterMark(x,tradeSignal,oldWaterMark):
        """ Calculate HighWaterMark"""
        if tradeSignal==1:
            if x>oldWaterMark:
                hwMark=x
            else:
                hwMark=oldWaterMark
        else:
            if x<oldWaterMark:
                hwMark=x
            else:
                hwMark=oldWaterMark
        return hwMark
    
    @abc.abstractmethod
    def CalcTakeProfitLevel(self,highWaterMark,tradeSignal):
        pass
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
     