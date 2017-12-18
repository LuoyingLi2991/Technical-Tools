# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 08:48:52 2017
    % Jai's position sizer for his MA crossover model.
    % ADD:  +1 unit/week if p <= 2nd price low of prev week (LONGS)
    %       +1 unit/week if p >= 2nd price high of prev week(SHORTS)
    % REDUCE -1 unit/day if slowMA gradient changes direction until
    %        reachlowerRiskUnit (2 units). Remainder of positions 
    %        cut to zero at crossover. 

@author: luoying.li
"""
import numpy as np
from Weekly import Weekly


class PositionJai:
    def __init__(self,data,tradeSignal,gradientScore,maxRiskUnits, lowerRiskUnitBoundary):
        """Constructor"""
        self.dates=data.index.tolist()
        self.x=data[data.columns[0]].tolist()
        self.tradeSignal=tradeSignal
        self.gradientScore=gradientScore
        self.maxRiskUnits=maxRiskUnits
        self.weekObj=Weekly(self.dates,self.x)
        self.lowerRiskUnitBoundary=lowerRiskUnitBoundary
        self.Run()
    
    def Run(self):
        self.height=len(self.x)
        self.positionSeries=np.zeros(self.height)
        days=[(each.weekday()+2)%7 for each in self.dates]  # create series of numerical days Sun =1, Mon=2, ... 
        start=[j for j, d in enumerate(days) if d==2][0]  # Find the first Monday
        if start==0:  # if data starts on Monday we need to skip first week
            start=5   # as we need t-1 data
        finish=[j for j, d in enumerate(days) if d==6][-1]  # find the last Friday of the series
        
        for i in range(start, finish+1, 5): # Start A New Week
            addPosition=False  # flag to ensure that you can't add more than 1 Unit of Risk a Week
            # Check Week Ahead
            if i+5>=self.height:  # Check that there is a full week ahead (i.e. NOT coming to end of series)
                weekAhead=self.height-i-1
            else:
                weekAhead=4  # full week ahead
            
            for j in range(i,i+weekAhead+1):  # loop through week
                # Check if New Trade
                if self.tradeSignal[j]!=self.tradeSignal[j-1]:
                    self.positionSeries[j]=self.tradeSignal[j]
                else:
                    # If In Existing Trade, Check to ADD POSITION
                    if abs(self.positionSeries[j-1])<self.maxRiskUnits: # % check that positions have not reached max yet
                        if not addPosition: # check that positions have not already been added this week
                            # LONGS
                            if self.tradeSignal[j]==1:
                                if self.x[j]<=self.weekObj.low2[j]: # check if below the 2nd low of the week
                                    self.positionSeries[j]=self.positionSeries[j-1]+1 # ADD LONG POSITION!!
                                    addPosition=True  # Flag to prevent further position increases
                                else:
                                    self.positionSeries[j]=self.positionSeries[j-1]  # Keep position
                            # SHORTS
                            if self.tradeSignal[j]==-1:
                                if self.x[j]>=self.weekObj.high2[j]:  # check if above the 2nd high of the week
                                    self.positionSeries[j]=self.positionSeries[j-1]-1  # ADD SHORT POSITION!! 
                                    addPosition=True  # Flag to prevent further position increases
                                else:
                                    self.positionSeries[j]=self.positionSeries[j-1] # Keep position
                            # FLAT
                            if self.tradeSignal[j]==0:
                                self.positionSeries[j]=0
                        else: # Positions have not been added => same position as yesterday
                            self.positionSeries[j]=self.positionSeries[j-1]
                    else: # max position reached aleady ....
                        self.positionSeries[j]=self.positionSeries[j-1]
                    # Check to REDUCE POSITION
                    if abs(self.positionSeries[j])>self.lowerRiskUnitBoundary: # only Reduce positions if > +/-2 
                        # Long
                        if self.tradeSignal[j]==1 and self.gradientScore[j]==-1:
                            self.positionSeries[j]=self.positionSeries[j-1]-1 # REDUCE LONG POSITION
                        # Short
                        if self.tradeSignal[-1] and self.gradientScore[j]==1:
                            self.positionSeries[j]=self.positionSeries[j-1]+1  # REDUCE SHORT POSITION
                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    