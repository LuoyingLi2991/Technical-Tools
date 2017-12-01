# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 11:21:56 2017
 Class for Moving Avgerages - Calculates SMA and EMA
     Class also calcs the MA's Gradient slope & the slope score.
     The x-axis of the gradient slope is determined in days and set by the user.
     Slope Score: +1: positive slope, -1: negative score.
     Class also calcs dev from MA (N.b. that if the assetType = 'bond' then we use minus for devFromMA)
     
    
     Methods
     -------
     checkTimeSeries() - Cleans data; splits up dates and x (Private)
     getGradient() - Constructs Gradient Object
     resetGradientMeasure() - Reset the gradient Window (changing all data)
     calcDevFromMA() - Deviation from MA (bonds: minus, else: %)
     calcToday() - calc today's readings MA level, dev from MA, Zscore,etc.

@author: luoying.li
"""
import sys
sys.path.append('P:\Python Library')  

import numpy as np
import pandas as pd
from UtilityClass import UtilityClass
from Gradient import Gradient


class MovingAverage():
    def __init__(self,data,MAType,MAWindow,**kwargs):
        self.data=data.fillna(method='bfill', axis=1)  # Single column dataframe 
        self.MAType=MAType
        self.MAWindow=MAWindow
        if kwargs!={}:
            keys=kwargs.keys()
        else:
            keys=[]
        if 'gradWindow' in keys:
            self.gradWindow=kwargs['gradWindow']
        else:  # if gradWindow is not specified
            self.gradWindow=1  # set Default
        if 'assetType' in keys:
            self.assetType=kwargs['assetType']
        else:
            self.assetType=None
        self.column=list(self.data)[0]
        self.CalcMA()
        self.TradeSignal=self.CalcTradeSignal()  # Calculate the Simple Score
        self.devFromMa=self.CalcDevFromMa()  # calc devFrom MA
        self.CalcToday()  # Today's Data
    def getGradient(self):
        """Constructs Gradient Object"""
        self.gg=Gradient(self.data['MA'].to_frame(),self.gradWindow)  # Create Gradient Object
        self.gradient=self.gg.Gradient  # actual gradient
        self.gradScore=self.gg.GradientScore  # gradient Score     
        self.gradDuration=self.gg.gradientDuration  # Duration of gradient
        self.TodayStatics['Gradient']=self.gradient[-1]  # today's gradient
        self.TodayStatics['GradientScore']=self.gradScore[-1]  # today's gradient score      
    def resetGradientMeasure(self,gradWindow):
        """Reset the gradient Window (changing all data)"""
        self.gradWindow=gradWindow
        self.gg.setGradientMeasure(gradWindow)
        self.gradient=self.gg.Gradient  # actual gradient
        self.gradScore=self.gg.GradientScore  # gradient Score     
        self.gradDuration=self.gg.gradientDuration  # Duration of gradient
        self.TodayStatics['Gradient']=self.gradient[-1]  # today's gradient
        self.TodayStatics['GradientScore']=self.gradScore[-1]  # today's gradient score
    def CalcMA(self):
        """inner factory for the appropriate MA method"""
        if self.MAType=="SMA":
            self.data['MA']=self.data.rolling(window=self.MAWindow).mean()
        if self.MAType=='EMA':
            a=(2.0/(1+self.MAWindow))
            self.data['MA']=self.data.ewm(alpha=a).mean()
        self.data.fillna(0,inplace=True)
    def CalcTradeSignal(self):
        """Calc Trade Signal"""
        temp=list(np.where(self.data['MA'] == 0, 0, np.where(self.data[self.column] >=self.data['MA'], 1, -1)))
        if self.MAType=='EMA':
            temp[0]=0
        self.data['signal']=temp
        return self.data['signal'].tolist()
    def CalcDevFromMa(self):
        """Deviation from MA (bonds: minus, else: %)"""
        if self.assetType=='bond':
            self.data['Dev']=np.where(self.data['MA']==0,0,self.data[self.column]-self.data['MA'])  # ignore the initial window 
        else:
            self.data['Dev']=np.where(self.data['MA']==0,0,((self.data[self.column]/self.data['MA'])-1)*100)
        return self.data['Dev'].tolist()
    def CalcToday(self):
        """Calc Today's Statistic"""
        dev=self.CalcDevFromMa()
        self.TodayStatics=self.data.iloc[-1].to_dict()  # ignore the first window
        dev=self.data['Dev'].to_frame()
        u=UtilityClass()
        z=u.calc_z_score(dev,False)
        self.TodayStatics['DevZscore']=z[1]
        

        
"""        
if __name__ == "__main__":
    data=pd.read_excel("c:\Book1.xlsx")
    data.set_index("Date",inplace=True)
    m=MovingAverage(data,"SMA",50)
    m.getGradient()
    print m.data.head()
    print m.TodayStatics
    print m.gradDuration
"""    

    

