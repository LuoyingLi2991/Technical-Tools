# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 10:40:20 2017
Class that calcs the time series of daily price high and low, given any intra-day
     frequency data. 
     There are also TWO OPTIONS too retrieve data:
     OPTION 1: Retrieves Yesterday's HiLo
     OPTION 2: Retieives the last 24hr
    
     Methods
     =======
     Set-Up() - Calcs the time series of Hi-Lo for each day.
    
     findYesterdayHiLo() - Given today's index, it finds yestsrday's HiLo.
        (N.b. since the number of obs of each day is not constant, we have 
          to a lookback search to ensure we correctly pick up yesterday's hilo
          and not a yesterday)

@author: luoying.li
"""
import pandas as pd
import numpy as np


class Daily():
    def __init__(self,data):
        """Constructor"""
        self.data=data
        self.dates=self.data.index.tolist()
        self.dailyHiLoData=[[]]*len(self.dates)
        if len(data.columns)>1:  # Check if Data Has Hi/Lo series
            self.x=self.data[self.data.columns[0]]
            self.xLo=self.data[self.data.columns[1]]
            self.xHi=self.data[self.data.columns[2]]
        else:  #  x is a single Price-close series
            self.x=self.data[self.data.columns[0]]
            self.xLo=self.data[self.data.columns[0]]
            self.xHi=self.data[self.data.columns[0]]
        self.SetUp()
    def SetUp(self):
        # create series of numerical days Sun =1, Mon=2, ... 
        days=[(each.weekday()+2)%7 for each in self.data.index.tolist()]
        k=1
        while k<=len(days)-2:
            if days[k]!=days[k-1] or k==1: # i.e. include first day)
                if k==1:
                    start=0  # Special Exception at the beginning of the series
                else:
                    start=k
                if days[k]<6: # Mon-Thurs                   
                    k=k+1
                    while days[k]==days[k-1] and k<=len(days)-2:  # Find out how many obs you have in the day
                        k=k+1
                else:
                    while days[k]>=6 and k<=len(days)-2:  # Fri or Sat
                        k=k+1
                oneDayHi=max(self.xHi[start:k])  # grab a days's data of highs and take the max
                oneDayLo=min(self.xLo[start:k])  # grab a days's data of lows and take the min
                oneDay=np.array([str(self.data.index[start]),oneDayLo,oneDayHi])
                oneDay=np.matlib.repmat(oneDay,k-start,1)  # copy and paste day multiple times
                for i in range(start,k):  # pass to the week container
                    self.dailyHiLoData[i]=self.dailyHiLoData[i]+list(oneDay[i-start][:])
                start=-1
        
        self.dailyHiLoData[-1]=self.dailyHiLoData[-2]  # Fill in Last Day of HiLo
                
    def findYesterdayHiLo(self,todayIndex):
        """findYesterdayHiLo"""
        today=self.dates[todayIndex]
        todayNum=(today.weekday()+2)%7  # Get Day Number
        i=todayIndex
        while (self.dates[i].weekday()+2)%7==todayNum and (self.dates[i].weekday()+2)%7!=7 and i>0:
            i=i-1  # Find yesterday's index
        hilo=self.dailyHiLoData[i][1:3]
        return hilo
    def find24hrHiLo(self,todayIndex):
        """find24hrHiLo"""
        findTheHour=self.dates[todayIndex].hour # Find the hr of the day
        i=todayIndex-2
        while self.dates[i].hour!=findTheHour and i>0: # Avoids a 'NullPointException' for min24 and max24 
            i=i-1
        min24=min(self.xLo[i+1:todayIndex])  # i+1 => ensure only go back 24hr
        max24=max(self.xHi[i+1:todayIndex])  # todayIndex-1 => start the window the hr before now 
        hilo=[min24,max24]
        return hilo


if __name__ == "__main__":
    data=pd.read_excel("c:\Book1.xlsx",'Sheet3')
    data.set_index("Date",inplace=True)
    s=Daily(data)
    print s.findYesterdayHiLo(20)
    print s.find24hrHiLo(20)
                              
