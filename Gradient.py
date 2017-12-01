# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 11:56:16 2017
Class that calculates gradient data of a time series (usually a MA) 
@author: luoying.li
"""
import numpy as np

class Gradient():
    def __init__(self,data,gradWindow):
        self.data=data
        self.gradWindow=gradWindow  # reset the gradient Window 
        self.Gradient=self.CalcGradient()
        self.GradientScore=self.CalcGradientScore()
        self.gradientDuration=self.CalcGradientDuration()
    def CalcGradient(self):
        """Calc Gradient"""
        name=list(self.data)[0]
        i=self.data[name].nonzero()[0][0]
        self.data['Gradient']=self.data[name].diff(self.gradWindow)  # the gradient series
        self.data['Gradient'].iloc[:i+self.gradWindow]=0  #  cut out initial MA window + GradientWindow
        return self.data['Gradient'].tolist()
    def CalcGradientScore(self):
        """Calc Gradient Score"""
        self.data['GradientScore']=np.where(self.data['Gradient']>0,1 ,np.where(self.data['Gradient']<0,-1,0))  # Attribute +1 score to positive gradient scores
        return self.data['GradientScore'].tolist()                                                              # Attribute -1 score to neg gradients
    def CalcGradientDuration(self):
        """Calc GradientDuration"""
        if self.data['GradientScore'].iloc[-1]==1:  # Number of Long Positive Grad Days
            idx=self.data[self.data['GradientScore']<1].index[-1]
            i=len(self.data[: idx])
            days=len(self.data)-i
        elif self.data['GradientScore'].iloc[-1]==-1:  # Number of Short Negative Grad Days
            idx=self.data[self.data['GradientScore']>-1].index[-1]
            i=len(self.data.loc[: idx])
            days=len(self.data)-i
        else:
            days=0
        return days
    
    def setGradientMeasure(self,gradWindow):
        """ResetGradientMeasure"""
        self.gradWindow=gradWindow
        self.Gradient=self.CalcGradient()
        self.GradientScore=self.CalcGradientScore()
        self.gradientDuration=self.CalcGradientDuration()
        