# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 17:58:51 2017
    % Standard Positioning-Incrementing Class 
    %   Detailed explanation goes here
    addPositionCondition:  % What % increase in price to add risk unit.
@author: luoying.li
"""

import numpy as np


class Position:
    def __init__(self,data,tradeSignal,addPositionCondition,maxRiskUnits):
        """Constructor"""
        self.date=data.index.tolist()
        self.x=data[data.columns[0]]
        self.tradeSignal=tradeSignal
        self.maxRiskUnits=maxRiskUnits
        self.addPositionCondition=addPositionCondition
        self.Run()
    
    def Run(self):
        """Runs The Position Series"""
        self.positionSeries=np.zeros(len(self.x))
        for i in range(1,len(self.x)):
            # Is Neutral
            if self.tradeSignal[i-1]==0:
                if self.tradeSignal[i]==1:  # Go Long
                    self.positionSeries[i]=1
                    latestTradeEntry=self.x[i]
                elif self.tradeSignal[i]==-1:  # Go Short
                    self.positionSeries[i]=-1
                    latestTradeEntry=self.x[i]
                else:  # Stay Neutral              
                    self.positionSeries[i]=0
            # Is Long
            if self.tradeSignal[i-1]==1:
                if self.tradeSignal[i]==1:  # Stay Long
                    checkPriceMove=self.CheckAddPosition(self.tradeSignal[i],latestTradeEntry,i)
                    if checkPriceMove and self.positionSeries[i-1]<self.maxRiskUnits:
                        self.positionSeries[i]=self.positionSeries[i-1]+1  # Add Poisition
                    else:
                        self.positionSeries[i]=self.positionSeries[i-1]
                elif self.tradeSignal[i]==0:  # Close. Go Neutral
                    self.positionSeries[i]=0
                else:
                    self.positionSeries[i]=-1  # Reverse Postion Go Short
            # Is Short
            if self.tradeSignal[i-1]==-1:
                if self.tradeSignal[i]==-1: # Stay Short
                    checkPriceMove=self.CheckAddPosition(self.tradeSignal[i],latestTradeEntry,i)
                    if checkPriceMove and self.positionSeries[i-1]>-self.maxRiskUnits:
                        self.positionSeries[i]=self.positionSeries[i-1]-1 # Add Poisition
                    else:
                        self.positionSeries[i]=self.positionSeries[i-1]
                elif self.tradeSignal[i]==0:  # Close. Go Neutral
                    self.positionSeries[i]=0
                else:  # Reverse Postion Go Long
                    self.positionSeries[i]=1
    
    def CheckAddPosition(self,tradeDirection,latestTradeEntry,i):
        """Checks when to Add Position if Exceed certain move"""
        priceMove=((self.x[i]/latestTradeEntry)-1)*100
        
        if tradeDirection==1:
            if priceMove>=self.addPositionCondition:
                addPosition=True
            else:
                addPosition=False
        else:
            if -priceMove>=self.addPositionCondition:
                addPosition=True
            else:
                addPosition=False
        return addPosition
    
                    
                    