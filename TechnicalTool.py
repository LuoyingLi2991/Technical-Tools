# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 14:53:40 2017

@author: luoying.li
"""
import sys
sys.path.append('P:\Python Library')  
import xlwings as xw
import pandas as pd
import numpy as np
from DataBaseConnection import DataBaseConnection
from JaiTrader import JaiTrader
from DoubleMA import DoubleMA
from Turtle import Turtle
from Position import Position
from PositionJai import PositionJai
from StopLossFactory import StopLossFactory
from TradeAnalysis import TradeAnalysis
from TakeProfitFactory import TakeProfitFactory
from PortfolioAnalysis import PortfolioAnalysis



def DownLoadData(FX,Freq,LBW):
    """Download Data from TradeStorage database"""
    # Construct tablename
    if len(FX)>6 and FX[-6:]=='Curncy':
        tablename=FX+Freq
    else:
        tablename=FX+'Curncy'+Freq
    path='P:\Interest Rate Model\TradeStorage' # default path to database
    Conn=DataBaseConnection(path,"TradeStorage.accdb")  # Connect to the database
    data=Conn.Read2DF(tablename,LB=LBW) # Extract data to dataframes
    data=data.values()[0]
    # Just Get Close price and form a dataframe
    if Freq=='Daily': 
        data=data['PX_LAST']
        if isinstance(data,pd.Series):
            data=data.to_frame()
    if Freq=='Hour':
        data=data['Close']
        if isinstance(data,pd.Series):
            data=data.to_frame()
    return data



def CalcStopContainers(model,gridStopChoice,tradeModel,addPositionCondition,maxPositionSize):
    """Construct Stop Tables for Grid Search sheet"""
    # Construct Stop Levels
    temp=range(1,9)
    stopLevels=[j*0.5 for j in temp]
    # Convert data to dataframe
    Data=pd.DataFrame(model.x,index=model.dates,columns=['Price'])
    gridStop1Container = np.zeros((8, 8))
    gridStopAllContainer = np.zeros((8,8))
    
    for k,i in enumerate(stopLevels):
        # Process data through stoploss and takeprofit
        ss=StopLossFactory.getInstance(gridStopChoice,Data,model.tradeSignal,i)
        data=pd.DataFrame(ss.stopFilteredFX,index=ss.dates,columns=['Price'])
        tp=TakeProfitFactory.getInstance('Dummy',data,ss.stopFilteredSignal)
        data=pd.DataFrame(tp.takeProfitFilterFX,index=model.dates,columns=['Price'])
        
        if tradeModel=='Jai':
            pp=PositionJai(data,tp.takeProfitFilterSignal,model.slowGradientSignal,maxPositionSize,2)
        else:
            pp=Position(data,tp.takeProfitFilterSignal,addPositionCondition,maxPositionSize)
        rr=TradeAnalysis(data,pp.positionSeries,maxPositionSize)
        # Extract analysed results of the first unit
        gridStop1Container[0,k]=rr.aggSharpeRatios[0][0]
        #print rr.aggSharpeRatios[0][0]
        gridStop1Container[1,k]=rr.totalPnL[0][0]
        gridStop1Container[2,k]=rr.winRatio[0][0]
        gridStop1Container[3,k]=rr.avgPnL[0][0]
        gridStop1Container[4,k]=rr.avgWinPnL[0][0]
        gridStop1Container[5,k]=rr.avgLossPnL[0][0]
        gridStop1Container[6,k]=- rr.avgWinPnL[0][0]/rr.avgLossPnL[0][0]
        gridStop1Container[7,k]=rr.maxDrawdown[0]
        #print gridStop1Container
        # Extract analysed results of the all units
        gridStopAllContainer[0,k]=rr.aggSharpeRatios[0][-1]
        gridStopAllContainer[1,k]=rr.totalPnL[0][-1]
        gridStopAllContainer[2,k]=rr.winRatio[0][-1]
        gridStopAllContainer[3,k]=rr.avgPnL[0][-1]
        gridStopAllContainer[4,k]=rr.avgWinPnL[0][-1]
        gridStopAllContainer[5,k]=rr.avgLossPnL[0][-1]
        gridStopAllContainer[6,k]=- rr.avgWinPnL[0][-1]/rr.avgLossPnL[0][-1]
        gridStopAllContainer[7,k]=rr.maxDrawdown[-1]
        
    return gridStop1Container, gridStopAllContainer
    

def CalcTakeProfitContainers(model,ss,gridTakeProfitChoice,gridTakeProfitPnLRule,tradeModel,maxPositionSize,addPositionCondition):
    """Construct TakeProfit tables for Grid Search sheet"""
    temp=range(1,9)
    tpLvls=[i*0.5 for i in temp]
    gridTakeProfit1Container = np.zeros((8, 8))
    gridTakeProfitAllContainer = np.zeros((8, 8))
    k=0
    for i in tpLvls:
        # process data through takeprofit
        data=pd.DataFrame(ss.stopFilteredFX,index=ss.dates,columns=['Price'])
        tp=TakeProfitFactory.getInstance(gridTakeProfitChoice,data,ss.stopFilteredSignal,i,gridTakeProfitPnLRule)
        data=pd.DataFrame(tp.takeProfitFilterFX,index=ss.dates,columns=['Price'])
        if tradeModel=='Jai':
            pp=PositionJai(data,tp.takeProfitFilterSignal,model.slowGradientSignal,maxPositionSize,2)
        else:
            pp=Position(data,tp.takeProfitFilterSignal,addPositionCondition,maxPositionSize)
        
        rr=TradeAnalysis(data,pp.positionSeries,maxPositionSize)
        # Extract analysed results of the first unit
        gridTakeProfit1Container[0,k]=rr.aggSharpeRatios[0][0]
        gridTakeProfit1Container[1,k]=rr.totalPnL[0][0]
        gridTakeProfit1Container[2,k]=rr.winRatio[0][0]
        gridTakeProfit1Container[3,k]=rr.avgPnL[0][0]
        gridTakeProfit1Container[4,k]=rr.avgWinPnL[0][0]
        gridTakeProfit1Container[5,k]=rr.avgLossPnL[0][0]
        gridTakeProfit1Container[6,k]=- rr.avgWinPnL[0][0]/rr.avgLossPnL[0][0]
        gridTakeProfit1Container[7,k]=rr.maxDrawdown[0]
        # Extract analysed results of the all units
        gridTakeProfitAllContainer[0,k]=rr.aggSharpeRatios[0][-1]
        gridTakeProfitAllContainer[1,k]=rr.totalPnL[0][-1]
        gridTakeProfitAllContainer[2,k]=rr.winRatio[0][-1]
        gridTakeProfitAllContainer[3,k]=rr.avgPnL[0][-1]
        gridTakeProfitAllContainer[4,k]=rr.avgWinPnL[0][-1]
        gridTakeProfitAllContainer[5,k]=rr.avgLossPnL[0][-1]
        gridTakeProfitAllContainer[6,k]=- rr.avgWinPnL[0][-1]/rr.avgLossPnL[0][-1]
        gridTakeProfitAllContainer[7,k]=rr.maxDrawdown[-1]
        
        k=k+1
    return gridTakeProfit1Container,gridTakeProfitAllContainer
        
def SlTpComb(Types,model,gridTakeProfitLevel,gridTakeProfitPnLRule,gridStopLevel,tradeModel,addPositionCondition,maxPositionSize):
    """Generic function that conduct analyse with different stoploss and takeprofit combination"""
    data=pd.DataFrame(model.x,index=model.dates,columns=['Price'])
    ss=StopLossFactory.getInstance(Types[0],data,model.tradeSignal,gridStopLevel)
    data=pd.DataFrame(ss.stopFilteredFX,index=ss.dates,columns=['Price'])
    tp=TakeProfitFactory.getInstance(Types[1],data,ss.stopFilteredSignal,gridTakeProfitLevel,gridTakeProfitPnLRule)
    data=pd.DataFrame(tp.takeProfitFilterFX,index=ss.dates,columns=['Price'])
    if tradeModel=='Jai':
        pp=PositionJai(data,tp.takeProfitFilterSignal,model.slowGradientSignal,maxPositionSize,2)
    else:
        pp=Position(data,tp.takeProfitFilterSignal,addPositionCondition,maxPositionSize)

    rr=TradeAnalysis(data, pp.positionSeries,maxPositionSize)
    return rr

@xw.sub
def GridSearchGenerator():
    """Macro that generate tables in GridSearch sheet"""
    wb = xw.Book.caller()
    temp=wb.sheets['GridSearch'].range('B1').value
    LB=wb.sheets['GridSearch'].range('F1').value
    FX=temp.split(" ")[0]
    Freq=temp.split(" ")[1]
    data=DownLoadData(FX,Freq,LB)
    data=data.fillna(method='bfill', axis=1) 
    tradeModel=wb.sheets['GridSearch'].range('D1').value
    
    # Default Settings
    maxPositionSize=5
    highFreqMA = 7
    lowFreqMA=25
    addPositionCondition = 1
    
    # Run Selected Model
    if tradeModel=='Jai':
        model=JaiTrader(data,'EMA',highFreqMA,1,'EMA',lowFreqMA,1,1,1)
    elif tradeModel=='DoubleMA':
        model=DoubleMA(data,'EMA',highFreqMA,1,'EMA',lowFreqMA,1,1)
    elif tradeModel=='MA':
        model=DoubleMA(data,'SMA',highFreqMA,1,'SMA',lowFreqMA,1,1)
    
    
    # Calc Stops Performance
    gridStopChoice=wb.sheets['GridSearch'].range('C10').value
    [gridStop1Container, gridStopAllContainer]=CalcStopContainers(model,gridStopChoice,tradeModel,addPositionCondition,maxPositionSize)
    
    wb.sheets['GridSearch'].range('D15').value=gridStop1Container
    wb.sheets['GridSearch'].range('P15').value=gridStopAllContainer

    # Calc TakeProfit Performance
    gridTakeProfitChoice=wb.sheets['GridSearch'].range('I28').value
    gridTakeProfitPnLRule=wb.sheets['GridSearch'].range('K28').value
    gridStopLevel=wb.sheets['GridSearch'].range('E28').value
    
    ss = StopLossFactory.getInstance(gridStopChoice,data, model.tradeSignal, gridStopLevel)
    [gridTakeProfit1Container,gridTakeProfitAllContainer]=CalcTakeProfitContainers(model,ss,gridTakeProfitChoice,gridTakeProfitPnLRule,tradeModel,maxPositionSize,addPositionCondition)
    
    wb.sheets['GridSearch'].range('D33').value=gridTakeProfit1Container
    wb.sheets['GridSearch'].range('P33').value=gridTakeProfitAllContainer
    
    # Time Series of Trades
    gridTakeProfitLevel=wb.sheets['GridSearch'].range('C44').value
    # No Stop, No Take Profit
    Types=['Dummy','Dummy']
    rr=SlTpComb(Types,model,gridTakeProfitLevel,gridTakeProfitPnLRule,gridStopLevel,tradeModel,addPositionCondition,maxPositionSize)
    n=len(rr.tradeContainer[:,0])
    tradeSeries=np.zeros((n,4))
    tradeSeries[:,0]=rr.tradeContainer[:,0]
    #print rr.tradeEntryExitIndex[-10:]
    tradeSeries[:,1]=rr.tradeContainer[:,5]
    # Stop, No Take Profit
    Types=[gridStopChoice,'Dummy']
    rr=SlTpComb(Types,model,gridTakeProfitLevel,gridTakeProfitPnLRule,gridStopLevel,tradeModel,addPositionCondition,maxPositionSize)
    
    tradeSeries[:,2]=rr.tradeContainer[:,5]
    # Stop and Take Profit
    Types=[gridStopChoice,gridTakeProfitChoice]
    rr=SlTpComb(Types,model,gridTakeProfitLevel,gridTakeProfitPnLRule,gridStopLevel,tradeModel,addPositionCondition,maxPositionSize)
    if len(rr.tradeContainer[:,5])>n:
        tradeSeries[:,3]=rr.tradeContainer[:n,5]
    else:
        tradeSeries[:,3]=rr.tradeContainer[:,5]
    
    
    wb.sheets['GridSearch'].range('AQ45:AT1000').clear_contents()
    # export trade series to sheet
    wb.sheets['GridSearch'].range('AQ45').value=tradeSeries
    
    # Generate histogram data
    binRange=np.arange(-0.05,0.26,0.01)
    binCounts=np.zeros((31,3))
    binCounts[:-1,0]=np.histogram(tradeSeries[:,1],binRange)[0]
    binCounts[:-1,1]=np.histogram(tradeSeries[:,2],binRange)[0]
    binCounts[:-1,2]=np.histogram(tradeSeries[:,3],binRange)[0]
    histoData=np.hstack((np.reshape(binRange,(31,1)),binCounts))
    
    wb.sheets['GridSearch'].range('AW45').value=histoData
    #wb.macro('GridPlots')
    
@xw.sub
def TradeReport():
    """Macro generate trade report for tradereport sheet""" 
    wb = xw.Book.caller()
    temp=wb.sheets['Report'].range('B1').value
    LB=wb.sheets['Report'].range('B2').value
    FX=temp.split(' ')[0]
    Freq=temp.split(' ')[1]
    tradeModel=wb.sheets['Report'].range('D1').value
    maxPositionSize=int(wb.sheets['Report'].range('B3').value)
    data=DownLoadData(FX,Freq,LB)
    data=data.fillna(method='bfill', axis=1) 
    
    # Default Settings
    highFreqMA = 7
    lowFreqMA=25
    addPositionCondition = 1
    
    # Run Selected Model
    if tradeModel=='Jai':
        model=JaiTrader(data,'EMA',highFreqMA,1,'EMA',lowFreqMA,1,1,1)
    elif tradeModel=='DoubleMA':
        model=DoubleMA(data,'EMA',highFreqMA,1,'EMA',lowFreqMA,1,1)
    elif tradeModel=='MA':
        model=DoubleMA(data,'SMA',highFreqMA,1,'SMA',lowFreqMA,1,1)
    
    # Get StopLoss and Take Profit parameters
    stopChoice=wb.sheets['Report'].range('D2').value
    stopLevel=wb.sheets['Report'].range('D3').value
    
    takeProfitChoice=wb.sheets['Report'].range('F1').value
    takeProfitLevel=wb.sheets['Report'].range('F2').value
    takeProfitPnL=wb.sheets['Report'].range('F3').value
    # Analyse data
    Types=[stopChoice,takeProfitChoice]
    rr=SlTpComb(Types,model,takeProfitLevel,takeProfitPnL,stopLevel,tradeModel,addPositionCondition,maxPositionSize)
    n=len(rr.tradeContainer[:,0])
    wb.sheets['Report'].range('A19:M10000').clear_contents()
    # Export results
    Results=np.zeros((n,13))
    Results[:,0]=rr.tradeContainer[:,0]
    indx=data.index.tolist()
    
    Results[:,3]=rr.tradeContainer[:,2]
    Results[:,4]=rr.tradeContainer[:,1]
    Results[:,5:]=rr.tradeContainer[:,3:]
    
    wb.sheets['Report'].range('A19').value=Results
    
    Dates=[]
    for i in range(n):
        Entry=indx[rr.tradeEntryExitIndex[i,1]]
        Exit=indx[rr.tradeEntryExitIndex[i,2]]
        Dates.append([Entry,Exit])

    wb.sheets['Report'].range('B19').value=Dates
    
    RU=[]
    RU.append([rr.aggSharpeRatios[0][0],rr.aggSharpeRatios[0][-1]])
    RU.append([rr.totalPnL[0][0],rr.totalPnL[0][-1]])
    RU.append([rr.winRatio[0][0],rr.winRatio[0][-1]])
    RU.append([rr.avgPnL[0][0],rr.avgPnL[0][-1]])
    RU.append([rr.avgWinPnL[0][0],rr.avgWinPnL[0][-1]])
    RU.append([rr.avgLossPnL[0][0],rr.avgLossPnL[0][-1]])
    RU.append([- rr.avgWinPnL[0][0]/rr.avgLossPnL[0][0],-rr.avgWinPnL[0][-1]/rr.avgLossPnL[0][-1]])
    RU.append([rr.maxDrawdown[0],rr.maxDrawdown[-1]])
    
    wb.sheets['Report'].range('E7').value=RU


def ModelAnalyse(data,paraDict):
    """Analysis data starting from generating trading signals from trade model"""
    # Default Settings
    highFreqMA = 7
    lowFreqMA=25
    addPositionCondition = 1
    
    outWindow=20
    inWindow=10
    # Get trade Model and trade Signal
    if paraDict['tradeType']=='Jai':
        model=JaiTrader(data,'EMA',highFreqMA,1,'EMA',lowFreqMA,1,1,1)
    elif paraDict['tradeType']=='DoubleMA':
        model=DoubleMA(data,'EMA',highFreqMA,1,'EMA',lowFreqMA,1,1)
    elif paraDict['tradeType']=='MA':
        model=DoubleMA(data,'SMA',highFreqMA,1,'SMA',lowFreqMA,1,1)
    elif paraDict['tradeType']=='Turtle':
        model=Turtle(data,outWindow,inWindow)
    # Analyse with stop loss and take profit choices
    Types=[paraDict['stopType'],paraDict['takeProfitType']]
    stopLevel=paraDict['stop']
    takeProfitLevel=paraDict['takeProfitRule']
    takeProfitPnL=paraDict['takeProfitPnLRule']
    tradeModel=paraDict['tradeType']
    maxPositionSize=int(paraDict['maxRiskUnits'])
    
    rr=SlTpComb(Types,model,takeProfitLevel,takeProfitPnL,stopLevel,tradeModel,addPositionCondition,maxPositionSize)
    return rr



@xw.sub
def TradePortfolio():
    """Analyse portfolio of trades for Portfolio sheet"""
    wb = xw.Book.caller()
    wb.sheets['Portfolio'].range('AY4:ES10000').clear_contents()
    temp=wb.sheets['Portfolio'].range('AI4:AS19').value
    LB=wb.sheets['Portfolio'].range('Z1').value
    # Get initial portfolio choices from Excel
    tradeData=pd.DataFrame(temp[1:],columns=temp[0])
    tradeData.set_index(tradeData.columns[0],inplace=True)
    
    # Analyse Data 
    n=len(tradeData)
    titleContainer=[]
    riskContainer=[]
    curIndex=[]
    cumulReturnsContainer=[]
    for i in range(n):
        if tradeData['liveTrade'].iloc[i]: # Check if FX was selected or not
            data=DownLoadData(tradeData['FX'].iloc[i],'Daily',LB)
            data=data.fillna(method='bfill', axis=1)
            if len(curIndex)==0:
                curIndex=curIndex+data.index.tolist()
            else:
                temp=list(set(curIndex) & set(data.index.tolist()))
                temp.sort()
                sq=[curIndex.index(t) for t in temp]
                cumulReturnsContainer=cumulReturnsContainer[sq]
                curIndex=temp
            data=data.loc[curIndex]
            paraDict=tradeData.iloc[i].to_dict()
            rr=ModelAnalyse(data,paraDict)  # Go through analysis process
            if len(cumulReturnsContainer)==0:
                cumulReturnsContainer=rr.cumulReturns
            else:
                cumulReturnsContainer=np.hstack((cumulReturnsContainer,rr.cumulReturns))
            for j in range(int(paraDict['maxRiskUnits'])):
                titleContainer.append(paraDict['FX'])
                riskContainer.append(j+1)
    titles=[t[:3]+'Risk'+str(c) for t,c in zip(titleContainer,riskContainer)]
    numTradeUnits=len(titleContainer)
    portfolioReturns=cumulReturnsContainer.sum(1)/numTradeUnits # compute portfolio returns
    
    # Analyse portfolio returns
    portReturnObj=PortfolioAnalysis(portfolioReturns)
    sharpe=portReturnObj.sharpeRatio
    totalReturn = portReturnObj.totalReturn  # the final return at the end of the series.
    annReturn = portReturnObj.annualizedReturn  # annualizerd Return over the period
    maxReturn = portReturnObj.maxReturn
    minReturn = portReturnObj.minReturn
            
    drawDownSeries = portReturnObj.drawDownSeries  # time series of drawdown
    maxDrawDown =  portReturnObj.maxDrawDown  # max drawdown

    cumulRet=pd.DataFrame(cumulReturnsContainer,index=data.index.tolist(),columns=titles)
    
    portRet=pd.DataFrame(portfolioReturns,index=data.index.tolist(),columns=['Total'])
    portRet['DrawDown']=drawDownSeries
    portRet.index.name='Dates'
    cumulRet.index.name='Dates'
    
    # export process data to sheet
    wb.sheets['Portfolio'].range('AY4').value=portRet
    wb.sheets["Portfolio"].range("BB4").value=cumulRet
    
    ratios=[sharpe,totalReturn,annReturn,maxReturn,minReturn,maxDrawDown[0]]
    wb.sheets['Portfolio'].range('Y35').value=ratios
    


