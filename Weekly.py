# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 11:33:29 2017
% Class that calcs the price high, 2nd high, low & 2nd low in each week
@author: luoying.li
"""
import numpy as np
import pandas as pd


class Weekly:
    def __init__(self,dates,x):
        self.dates=dates
        self.x=x
        self.SetUp()
    
    def SetUp(self):
        height=len(self.x)
        weekData=np.zeros((height,5))
        days=[(each.weekday()+2)%7 for each in self.dates]  # create series of numerical days Sun =1, Mon=2, ... 
        start=[j for j, d in enumerate(days) if d==2][0]  # Find the first Monday
        finish=[j for j, d in enumerate(days) if d==6][-1]  # find the last Friday of the series
        for i in range(start,finish+1,5):
            week=self.x[i:i+5] # grab a week's data
            week.sort() # sort the data low to high price
            #print week
            week=np.matlib.repmat(week,5,1) # copy and paste (5 x 5)
            #print week
            weekData[i:i+5,:]=week  # pass to the week container

        weekData[5:,:]=weekData[:-5,:]
        weekData[:5,:]=0
        self.low1=weekData[:,0]
        self.low2=weekData[:,1]
        self.high1=weekData[:,3]
        self.high2=weekData[:,4]
        
