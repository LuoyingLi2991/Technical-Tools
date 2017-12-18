# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:56:02 2017
Class for working on two MA for analysis of MA crossover signals, 
     MA divergence/convergence and its corresponding signals  
     
    
     Methods
     -------
     checkTimeSeries(obj)- for dates
     calcCrossOverScore(obj)  - Calcs the crossover score (+1: FastMA>SlowMA, -1: FastMA<SlowMa)
     calcSpread(obj) - Calcs spread between fast and slow MA ( FastMA - SlowMA)
     calcSpreadGradient(obj, spreadGradWindow) - Uses a Gradient Object to Calc all data for the gradient of the spread
     plotMA(obj) - plots a simple graph of MAs
     calcTradeDaySeries() - Calcs Series of Trade days
     calcLastCrossOver() - calcs the level of the last Cross Over
     calcHiLoInCurrentTrade - calc the price hilo during the current trade [hi, lo]

@author: luoying.li
"""
import sys
sys.path.append('P:\Python Library')  

from MovingAverage import MovingAverage
from Gradient import Gradient
from UtilityClass import UtilityClass
import numpy as np
import pandas as pd


class DoubleMA():
    def __init__(self,data,fastType,fastWindow,fastGradWindow,slowType,slowWindow,slowGradWindow,spreadGradWindow):
        self.data=data.fillna(method='bfill', axis=1)
        self.x=self.data[self.data.columns[0]].tolist()
        self.dates=self.data.index.tolist()
        self.height=len(self.data)
        self.spreadGradWindow=spreadGradWindow
        self.TodayStatics={}
        
        self.slowType=slowType
        self.slowWindow=slowWindow
        self.slowGradWindow=slowGradWindow
        self.slowMAObj=MovingAverage(self.data,self.slowType,slowWindow,gradWindow=slowGradWindow)
        self.slowMA=self.slowMAObj.data['MA'].tolist()
    
        self.fastType=fastType
        self.fastWindow=fastWindow
        self.fastGradWindow=fastGradWindow
        self.fastMAObj=MovingAverage(self.data,self.fastType,fastWindow,gradWindow=fastGradWindow)
        self.fastMA=self.fastMAObj.data['MA'].tolist()
        self.tradeSignal=self.CalcCrossOverScore()
        self.spread = self.CalcSpread()
        self.CalcSpreadGradient()  # This will set all gradient data   
        self.tradeDaySeries=self.CalcTradeDaySeries()
        self.TodayStatics['todayMAslow']=self.slowMA[-1]  # today's level of the slow MA
        self.TodayStatics['todayMAfast']=self.fastMA[-1]  # today's level of the fast MA
        self.TodayStatics['todayCrossScore']=self.tradeSignal[-1]
        self.TodayStatics['todaySpread']=self.spread[-1]
        self.TodayStatics['todayTradeDays']=self.tradeDaySeries[-1]
        self.preCrossOver=self.CalcLastCrossOver()
        self.CalcTradeDayZscores()  # Calc Z-score of Trading days
        if (fastWindow>slowWindow):
            raise Exception('Parameter Error : fast MA is larger than slow MA')
        self.CalcHiLoInCurrentTrade()  # calculate the price hilo during current trade 
        
    def CalcCrossOverScore(self):
        """Calcs the crossover score (+1: FastMA>SlowMA, -1: FastMA<SlowMa)"""
        cross=np.where(self.fastMAObj.data['MA']>self.slowMAObj.data['MA'],1,-1)
        cross[:self.slowWindow-1]=0
        return list(cross)
    def CalcSpread(self):
        """Calcs spread between fast and slow MA ( FastMA - SlowMA)"""
        spread=(self.fastMAObj.data['MA']-self.slowMAObj.data['MA']).as_matrix()
        spread[:self.slowWindow-1]=0
        return spread
    def CalcSpreadGradient(self,*spreadGradWindow):  # pass spreadGradWindow so that it can be changed
        """Uses a Gradient Object to Calc all data for the gradient of the spread"""
        if not spreadGradWindow==():  # Set the GradientWindow
            self.spreadGradWindow=spreadGradWindow[0]
        data=pd.DataFrame(self.spread)
        gradObj=Gradient(data,self.spreadGradWindow)
        self.spreadGradient=gradObj.Gradient  # Create gradient series
        self.spreadGradientScore=gradObj.GradientScore  # Create gradient score
        self.TodayStatics['todayGrad']=self.spreadGradient[-1]   # today's gradient
        self.TodayStatics['todayGradScore']=self.spreadGradientScore[-1]  # today's gradient score.
    def CalcTradeDaySeries(self):
        trdays=np.zeros(self.height)
        for i in range(self.slowWindow,self.height):
            if not self.tradeSignal[i]==self.tradeSignal[i-1]:
                trdays[i]=self.tradeSignal[i]
            elif self.tradeSignal[i]==1:
                trdays[i]=trdays[i-1]+1
            elif self.tradeSignal[i]==-1:
                trdays[i]=trdays[i-1]-1
            else:
                trdays[i]=0
        return list(trdays)
    def CalcLastCrossOver(self):
        """calcs the level of the last Cross Over"""
        index=int(self.height-abs(self.tradeDaySeries[-1])-1)  # index pt in series that last crossover occurs
        if index<self.height:   #  defence block for no cross-overs (like for the VEB Curncy)
            crossSlow=np.zeros(2)
            crossSlow[0]=self.slowMA[index]  # slow y(t) - before the crossover   
            crossSlow[1]=self.slowMA[index+1]  # slow y(t+1) - after the crossover
            gradSlow=crossSlow[1]-crossSlow[0]  # gradient of slow MA
            
            crossFast=np.zeros(2)
            crossFast[0]=self.fastMA[index]  # fast y(t)
            crossFast[1]=self.fastMA[index+1]  # fast y(t+1)
            gradFast=crossFast[1]-crossFast[0]  # grad of fast MA
            
            xStar=(crossFast[0]-crossSlow[0])/(gradSlow-gradFast)  # at cross -> mx* + c = mx* + c
            lastCross=gradSlow*xStar+crossSlow[0]  # put x* back into y = mx* + c
        else:
            lastCross=self.height
        return lastCross
    def CalcTradeDayZscores(self):
        """Calcs the Z-Score of Trade Days"""
        td=np.array( self.tradeDaySeries)
        if self.tradeDaySeries[-1] is not 0:
            filterTradeZeros=list(td[td!=0])  # Exclude RangeDays (0)
            u=UtilityClass()
            df=pd.DataFrame(filterTradeZeros)
            self.tradeDays_Zscore=u.calc_z_score(df,False)[1]
        else:
            self.tradeDays_Zscore=0
    
    def CalcHiLoInCurrentTrade(self):
        """calc the price hilo during the current trade [hi, lo]"""
        self.currentTradeHiLo=np.zeros(2)
        if self.tradeSignal[-1]!=0:
            tradeStartIndex=np.where(self.tradeSignal!=self.tradeSignal[-1])[-1][-1]  # find when the current trade started
            currentTrade=self.data[self.data.columns[0]].tolist()[int(tradeStartIndex)+1:]
            self.currentTradeHiLo[0]= np.max(currentTrade)
            self.currentTradeHiLo[1]=np.min(currentTrade)

            

if __name__ == "__main__":
    data=pd.read_excel("c:\Book1.xlsx")
    data.set_index("Date",inplace=True)
    Dma=DoubleMA(data,'SMA',5,1,'SMA',10,1,5)
    #Dma.CalcHiLoInCurrentTrade()
    #print Dma.tradeDays_Zscore