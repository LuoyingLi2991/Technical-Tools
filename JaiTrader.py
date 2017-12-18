# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 09:55:44 2017
    % Jai MA crossover trading model. 
    % Entry:
    % -----
    % Long: crossover+1, slowMA gradient+1.
    % Short: crossover-1, slowMA gradient-1.
    %
    % Exit:
    % -----
    % Crossover in other direction
    % 
    cheat: %Boolean flag: +1: for trading on the same day. 0: for trading next day
@author: luoying.li
"""
from DoubleMA import DoubleMA
import numpy as np


class JaiTrader:
    def __init__(self,data,fastType,fastWindow,fastGradWindow,slowType,slowWindow,slowGradWindow,spreadGradWindow,cheat):
        """Constructor"""
        self.MA=DoubleMA(data,fastType,fastWindow,fastGradWindow,slowType,slowWindow,slowGradWindow,spreadGradWindow)
        self.x=self.MA.data[self.MA.data.columns[0]].tolist()
        self.dates=self.MA.data.index.tolist()
        self.height=self.MA.height
        self.crossOverSignal=self.MA.tradeSignal
        self.slowGradientSignal=self.MA.slowMAObj.gradScore
        self.cheat=cheat
        self.tradeSignal=self.Trade()
        self.todayCross=self.crossOverSignal[-1]
        self.todaySlowGradient=self.slowGradientSignal[-1]
        self.todayTradeSignal=self.tradeSignal[-1]
        self.tradeDuration=self.CalcTradeDuration()
    
    def Trade(self):
        t=np.zeros(self.height+1) # +1 extra day as last signal at the end of series was yesterday. need extra cell for today's score 
        
        for i in range(1,self.height+1):
            # If NEUTRAL
            if t[i-1]==0:
                if self.crossOverSignal[i-1]==1 and self.slowGradientSignal[i-1]==1:  # START LONG: Cross+1, Grad: +1
                    t[i]=1
                elif self.crossOverSignal[i-1]==-1 and self.slowGradientSignal[i-1]==-1:  # START SHORT: Cross-1, Grad-1
                    t[i]=-1
                else:
                    t[i]=0  # STAY NEUTRAL     
            # If LONG    
            elif t[i-1]==1:
                if self.crossOverSignal[i-1]==1: # STAY LONG Cross+1
                    t[i]=1
                elif self.crossOverSignal[i-1]==-1 and self.slowGradientSignal[i-1]==-1: # FLIP to SHORT: Cross-1, Grad-1 
                    t[i]=-1
                else:  # Go NEUTRAL: Crossover changed to -1
                    t[i]=0
            # If SHORT    
            elif t[i-1]==-1:
                if self.crossOverSignal[i-1]==-1: # STAY SHORT Cross-1
                    t[i]==-1
                elif self.crossOverSignal[i-1]==1 and self.slowGradientSignal[i-1]==1:  # FLIP to LONG: Cross+1, Grad+1 
                    t[i]=1
                else:  # Go NEUTRAL: Crossover changed to +1
                    t[i]=0
        if self.cheat==1: # check if you want to CHEAT
            t[:-1]=t[1:]
            t[-1]=t[-2]
        return t
    
    def CalcTradeDuration(self):
        """calcTradeDuration"""
        if self.todayTradeSignal==0:  # market is flat
            days=0
        else:
            index=[i for i, t in enumerate(self.tradeSignal) if t==-self.todayTradeSignal][-1]  # find last opposite trade
            days=self.height-index-1
            days=days*self.todayTradeSignal  # makes days neg if short signal
        return days