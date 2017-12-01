# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 10:24:49 2017
Super Class for Stop Loss. 
Class is abstract as it includes abstract method 
@author: luoying.li
"""

import abc
import numpy as np



class StopLoss:
     __metaclass__ = abc.ABCMeta
     # Constructor
     def __init__(self,data,tradeSignal):
         self.data=data
         self.height=len(data)
         self.tradeSignal=tradeSignal
         self.numTrades=self.CountTrades()
     def RunStopLoss(self):
         """StopLoss Filtering Process"""
         slFilter=[0]*self.height
         self.stopLossSeries=np.nan*np.ones((self.height,2))
         self.stopFilteredFX=self.data[self.data.columns[0]].tolist()  # Filtered FX starts with Original FX Series
         hitStopFlag=0  # Flag +1 if hit trade in the stop 
         self.stopContainer=np.zeros((self.numTrades,3))
         tradeNumber=0
         
         for i in range(1,self.height):
             # STOP NOT HIT
             if hitStopFlag==0:
                 # Neutral ->  Trade
                 if self.tradeSignal[i-1]==0 and abs(self.tradeSignal[i])>0:
                     tradeNumber=tradeNumber+1  # New Trade
                     hitStopFlag=0
                     self.stopLossSeries[i]=self.CalcStopLevel(self.data[self.data.columns[0]].iloc[i],self.tradeSignal[i])
                     slFilter[i]=self.tradeSignal[i]
                 
                 # Trade -> Neutral   
                 elif abs(self.tradeSignal[i-1])>0 and self.tradeSignal[i]==0:
                     self.BookTrade(tradeNumber,self.data[self.data.columns[0]].iloc[i],0)  # Book Trade
                     hitStopFlag=0
                     slFilter[i]=0
                 # Old Trade -> New Trade
                 elif self.tradeSignal[i]!=self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0 and abs(self.tradeSignal[i-1])>0:
                     # CHECK FIRST IF long TRADE HITS STOP BEFORE FLIP
                     if self.tradeSignal[i-1]==1 and self.data[self.data.columns[0]].iloc[i]<self.stopLossSeries[i-1,0]:
                         self.BookTrade(tradeNumber,max(self.stopLossSeries[i-1,:]),1)  # Close old Trade at Stop
                         self.stopFilteredFX[i]=max(self.stopLossSeries[i-1,:])  # Override FX Series with Stop
                     # CHECK FIRST IF short TRADE HITS STOP BEFORE FLIP
                     elif self.tradeSignal[i-1]==-1 and self.data[self.data.columns[0]].iloc[i]>self.stopLossSeries[i-1,1]:
                         self.BookTrade(tradeNumber, self.stopLossSeries[i-1,int(self.tradeSignal[i-1])],1)  # Close old Trade at Stop
                         self.stopFilteredFX[i]=self.stopLossSeries[i-1,int(self.tradeSignal[i-1])]  # Override FX Series with Stop
                     # Trade Flipped WITHOUT STOP BEING HIT 
                     else:
                         # Close old Trade
                         if self.tradeSignal[i-1]==-1:
                             self.BookTrade(tradeNumber,self.stopLossSeries[i-1,int(self.tradeSignal[i-1])],0)
                         else:
                             self.BookTrade(tradeNumber,max(self.stopLossSeries[i-1,:]),0)  
                     tradeNumber = tradeNumber + 1  # NEW TRADE
                     hitStopFlag = 0  # Reset for new Trade
                     self.stopLossSeries[i,:]=self.CalcStopLevel(self.data[self.data.columns[0]].iloc[i],self.tradeSignal[i])  # Set NEW Stop
                     slFilter[i]=self.tradeSignal[i]
                 
                 # Trade -> Trade
                 elif self.tradeSignal[i]==self.tradeSignal[i-1] and self.tradeSignal[i]!=0:
                     # CHECK IF long TRADE HITS STOP
                     if self.tradeSignal[i]==1 and self.data[self.data.columns[0]].iloc[i]<self.stopLossSeries[i-1,0]:
                         hitStopFlag=1  # Raise Flag!!! %% STOP HIT!!
                         self.BookTrade(tradeNumber,max(self.stopLossSeries[i-1,:]),1)  # Trade DID HIT STOP
                         self.stopFilteredFX[i]=max(self.stopLossSeries[i-1,:])  # Override FX Series with Stop
                         slFilter[i]=0  # Override and close trade
                     # CHECK IF short TRADE HITS STOP
                     elif self.tradeSignal[i]==-1 and self.data[self.data.columns[0]].iloc[i]>self.stopLossSeries[i-1,1]:
                         hitStopFlag=1
                         self.BookTrade(tradeNumber,self.stopLossSeries[i-1,int(self.tradeSignal[i])],1)  # Trade DID HIT TAKE PROFIT
                         self.stopFilteredFX[i]=self.stopLossSeries[i-1,int(self.tradeSignal[i])]  # Override FX Series with Stop 
                         slFilter[i]=0  # Override and close trade
                     # NO Stop Hit, Continue Trade
                     else:
                         hitStopFlag = 0; 
                         self.stopLossSeries[i,:] = self.stopLossSeries[i-1,:]  # Continue the Stop Level
                         slFilter[i] = self.tradeSignal[i]
             else:  # STOP HIT
                # Trade -> Trade = Suppress Signal 
                if self.tradeSignal[i]==self.tradeSignal[i-1]: 
                    hitStopFlag = 1
                    slFilter[i] = 0
                # Old Trade -> New Trade = End Signal Suppression
                elif self.tradeSignal[i]!=self.tradeSignal[i-1] and abs(self.tradeSignal[i])>0:
                    tradeNumber = tradeNumber + 1
                    hitStopFlag = 0
                    self.stopLossSeries[i,:] =self.CalcStopLevel(self.data[self.data.columns[0]].iloc[i],self.tradeSignal[i])  # Set Stop
                    slFilter[i] = self.tradeSignal[i]
         # Add last trade in series if it is still live           
         if (not np.all(self.stopContainer==0)) and self.stopContainer[-1,0]==0:
             if self.tradeSignal[-1]==-1:
                 self.BookTrade(tradeNumber, self.stopLossSeries[i-1,int(self.tradeSignal[-1])],0)
             else:
                 self.BookTrade(tradeNumber,max(self.stopLossSeries[i-1,:]),0)
         return slFilter
 
     
     def BookTrade(self,trNumber,stopLevel,hit):
         """bookTrade - Helps book the takeProfit data in the tradeContainer"""
         self.stopContainer[trNumber-1,0]=trNumber
         self.stopContainer[trNumber-1,1]=stopLevel
         self.stopContainer[trNumber-1,2]=hit  # 1: if Stop Hit, or 0: if due to change in trade signal. 
        
     def CalcStopRatio(self):
         """calc StopRatio"""
         numofStops=sum(self.stopContainer[: ,2])
         sr=numofStops/self.numTrades
         return sr
     
        
     def CountTrades(self):
         """Count Num of Trades"""
         count=0
         for i in range(1,self.height):
             if self.tradeSignal[i]!=self.tradeSignal[i-1]:
                 count=count+1
         return count
     

     @abc.abstractmethod
     def CalcStopLevel(self, entryLevel, tradeSignal):
         pass
     