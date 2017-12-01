# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 14:40:08 2017
This is a Static Class that obtains the hilo for a given trade window. 
  
     There are two formats for price series x().
           x() = [xClose]
     or
           x() = [xClose, xOpen, xhi, xlo]
    
     Static Methods
     --------------
     FormatData() - decomposes data into [Close, Open, High, Low]
           even if input is just xClose    
     CalcHiLoSeries() - Calcs the Series if hilo, given TradeWindow. 
           Note that the trade window does NOT INCLUDE TODAY. 
           i.e., it calculates the preceding N days. It starts 
           YESTERDAY and goes back from there.
           OUTPUT = dataframe with columns: dates, RollMin, RollMax
     CalcHiLo() Calcs the Series for a given Day and look-back window.
           Note that the trade window does NOT INCLUDE TODAY. It starts 
           YESTERDAY and goes back from there.
           OUTPUT = a list with [LOW, HIGH]    
     CalcRollStdDev() Calcs the Rolling stdDev over a given Rollback period

@author: luoying.li
"""
import pandas as pd


class LookBackWindow:
    @staticmethod
    def FormatData(data):
        """decomposes data into [Close, Open, High, Low]"""
        oldName=data.columns[0]
        data.rename(columns={oldName:'Close'},inplace=True)
        if len(data.columns)==1:
            data['Open']=data['Close']
            data['High']=data['Close']
            data['Low']=data['Close']
        return data

    @staticmethod
    def CalcHiLoSeries(data,window):
        """Calcs the Series if hilo, given TradeWindow"""
        data=LookBackWindow.FormatData(data)
        data['RollMin']=data['Low'].rolling(window).min().shift()
        data['RollMax']=data['High'].rolling(window).max().shift()
        rlt=data[['RollMin','RollMax']].fillna(0)  # Combine into a dataframe and fill NA with 0
        return rlt
    
    @staticmethod
    def CalcHiLo(data,dayIndex,window):
        """Calcs the Series for a given Day and look-back window."""
        data=LookBackWindow.FormatData(data)
        i=dayIndex-1 
        lo=data['Low'].iloc[i-window:i-1].min()
        hi=data['High'].iloc[i-window:i-1].max()
        return (lo,hi)
    @staticmethod
    def CalcRollStdDev(data,window):
        """Calcs the Rolling stdDev over a given Rollback period"""
        data['std']=data[data.columns[0]].rolling(window+1).std()
        rlt=data['std'].fillna(0).tolist()
        return rlt
    






    
""" 
if __name__ == "__main__":
    data=pd.read_excel("c:\Book1.xlsx")
    data.set_index("Date",inplace=True)
    lbw=LookBackWindow()
    print lbw.CalcRollStdDev(data,5)
"""    
    
        
        