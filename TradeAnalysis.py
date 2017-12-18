# -*- coding: utf-8 -*-
"""
Created on Mon Dec 04 09:13:30 2017
Generates results data for a trading model, given FX series, and the position series.
properties
        x; % price series
        dates %
        height % height of price series
        positionSeries % position series 
        maxPositionSize;  % maxPositionSize
        priceReturns; % NON LOG daily return of price series.
        
        modelReturns; % Matrix of DAILY (NON LOG)returns, each column representing the returns for each risk unit 1,2,3,4 ...
        cumulReturns; % Matrix of the cumulative GEOMETRIC returns run independently on each single risk unit 1,2,3,4 ... 
        aggregateModelReturns % Matrix of DAILY returns, each column representing the returns for each accumulated 1,1+2, 1+2+3 etc
        accumulatedModelReturns % Matrix of GEOMETRIC ACCUMULATED on the AGGREGATION of risk positions  1, 1+2, 1+2+3 
        
        tradeContainer % Contains meta for each trade and for each unit of position
                       % col1 = TradeNum; 
                       % col2 = max Pos Units in tradecol; 
                       % col3 = tradeDuration; 
                       % col4 = Win/Lose Indicator (Win: +1 Lose: 0)
                       % col5 = Running Win Ratio
                       %(col6:end)=PnL[] for each position +  PnL for all positions  
                       %                                                                                       
        numTrades % Number of Trades
        avgPosition % Avg Position Size Held
        avgTradeDuration % Avg Trade Duration (Days)
        winRatio % WinRatio (Scalar)
        totalPnL % Total PnL (Vector)
        avgPnL; % Avg PnL (Vector)
        avgWinPnL; % Avg PnL of Winning Trades (Vector)
        avgLossPnL; % Avg PnL of Losing Trades(Vector)
        tradeStats; % Container for each pos and total position of trades
                    % row 1: WinRatio
                    % row 2: Avg PnL
                    % row 3: Avg Win PnL
                    % row 4: Avg Loss PnL
        aggSharpeRatios; % sharpe ratios[] on returns on accumulated risk positions.
        drawDown % DrawDown[] Series of Accumulated Returns
        maxDrawdown % maxDrawdowns 
        tradeEntryExitIndex; % Index markers on the time series showing entry/exit points (used for graphing results)
        sharpeObj %Sharpe Obj (if u want to get decomp of avj return and ann. vol)
        intraTradeMinPnL % The Min PnL obtained (but not realized)during the life of each trade and for each Risk Unit. [numTrade x MaxPosSize] 
        intraTradeMaxPnL % The Max PnL obtained (but not realized)during the life of each trade and for each Risk Unit. [numTrades x MaxPosSize]       
 
@author: luoying.li
"""
import pandas as pd
import numpy as np
from SharpeRatio import SharpeRatio



class TradeAnalysis:
    def __init__(self,data,positionSeries,maxPositionSize):
        self.partition=6
        self.dates=data.index.tolist()
        x=data[data.columns[0]].tolist()
        self.x=self.CheckNan(x)
        self.height=len(data)
        self.positionSeries=positionSeries
        self.maxPositionSize=maxPositionSize
        self.priceReturns=self.CalcPriceReturn()
        self.modelReturns = self.CalcModelReturns()
        self.cumulReturns = self.CalcCumulReturns()
        self.aggregateModelReturns=self.CalcAggModelReturns()
        self.accumulatedModelReturns=self.CalcAccmulatedModelReturns()
        self.tradeContainer=self.CalcTrade()
        self.tradeStats=self.CalcTradeStats()
        self.aggSharpeRatios=self.CalcSharpeRatios()
        self.drawDown=self.CalcDrawdown()
        self.CalcIntraTradePnL()
        
    def CalcPriceReturn(self):
        """calcPriceReturns"""
        temp=pd.DataFrame(self.x)
        priceReturns=[each[0] for each in temp.pct_change().as_matrix()]
        priceReturns[0]=0
        return priceReturns
    
    def CalcModelReturns(self):
        """CalculateModelReturns"""
        modelReturns=np.zeros((self.height,self.maxPositionSize))
        for i in range(self.maxPositionSize):
            # capture long/short positions of size i
            pos=np.where(np.array(self.positionSeries)>i,1,np.where(np.array(self.positionSeries)<-i,-1,0))
            for j in range(1,self.height):
                modelReturns[j,i]=pos[j-1]*self.priceReturns[j]
        return modelReturns
    
    def CalcCumulReturns(self):
        """Geomtric returns for each individual risk unit"""
        cumulRet=np.zeros((self.height,self.maxPositionSize))
        cumulRet[0,:]=1+self.modelReturns[0,:]  # Initialization of first row = 1
        for i in range(1,self.height):
            cumulRet[i,:]=np.array(cumulRet[i-1,:])*(1+self.modelReturns[i,:])
        return cumulRet
    
    def CalcAggModelReturns(self):
        """The aggregation of daily returns across risk units"""
        aggModelReturns=np.zeros((self.height,self.maxPositionSize))
        aggModelReturns[:,0]=self.modelReturns[:,0]
        if self.maxPositionSize>1:  # if max position > 1
            for i in range(1,self.maxPositionSize):
                aggModelReturns[:,i]=aggModelReturns[:,i-1]+self.modelReturns[:,i]
        return aggModelReturns
    
    def CalcAccmulatedModelReturns(self):
        """The Accumulation of daily returns over time (GEOMETRIC)"""
        accumReturns=np.zeros((self.height,self.maxPositionSize))
        accumReturns[0,:]=1+self.aggregateModelReturns[0,:]
        for i in range(1,self.height):
            accumReturns[i,:]=accumReturns[i-1,:]*(1+self.aggregateModelReturns[i,:])
        return accumReturns
    
    def CalcTrade(self):
        """Calculate Trade Count + Duration + PNL"""
        trade=np.zeros((self.height,self.partition+self.maxPositionSize-1))
        self.tradeEntryExitIndex=np.zeros((self.height,3)).astype(int)
        tradeNum=0  # initialize trade number
        
        pos=self.positionSeries[0]  # Initialize start position 
        for i in range(1,self.height):
            # if yesterday flat
            if pos==0:
                #  new trade today!!
                if self.positionSeries[i]!=0:
                    tradeNum=tradeNum+1  # New Trade Number
                    entryIndex=i
                    pos=self.positionSeries[i]  # Trade Direction
                    PnL=np.ones((1,self.maxPositionSize))  # Reset PnL in Geometric form
                    tradeDays=1  # Reset tradeDays
                    posSize=self.positionSeries[i]  # Reset Pos Size
            # if yesterday in a position
            else:
                # position closed today
                if np.sign(self.positionSeries[i])==0:
                    trade[tradeNum-1,0]=tradeNum  # Book the Trade
                    trade[tradeNum-1,1]=posSize  
                    trade[tradeNum-1,2]=tradeDays
                    if pos>0:  # if long
                        PnL=PnL*(1+self.modelReturns[i,:])  # update PnL before closing
                        PnL=PnL-1  # transform out of geometric
                    else:  # if short
                        PnL=PnL*(1-self.modelReturns[i,:])
                        PnL=1-PnL
                    trade[tradeNum-1,self.partition-1:]=PnL
                    exitIndex=i
                    self.tradeEntryExitIndex[tradeNum-1,0:4]=[tradeNum,int(entryIndex),int(exitIndex)]
                    entryIndex=0
                    exitIndex=0
                    PnL=np.ones((1,self.maxPositionSize))  # Reset PnL
                    pos=0  # Reset current position to flat 
                # position flipped
                elif np.sign(self.positionSeries[i])!=np.sign(self.positionSeries[i-1]):
                    trade[tradeNum-1,0]=tradeNum  # Book the Trade
                    trade[tradeNum-1,1]=posSize
                    trade[tradeNum-1,2]=tradeDays
                    if pos>0:  # if long
                        PnL=PnL*(1+self.modelReturns[i,:])  # update PnL before closing
                        PnL=PnL-1
                    else:  # if short
                        PnL=PnL*(1-self.modelReturns[i,:])
                        PnL=1-PnL
                    trade[tradeNum-1,5:]=PnL
                    exitIndex=i
                    self.tradeEntryExitIndex[tradeNum-1,0:4]=[tradeNum,int(entryIndex),int(exitIndex)]
                    tradeNum=tradeNum+1
                    entryIndex=i
                    exitIndex=0
                    pos=self.positionSeries[i]
                    PnL=np.ones((1,self.maxPositionSize))
                    tradeDays=1
                    posSize=self.positionSeries[i]
                else:
                    if pos>0:
                        PnL=PnL*(1+self.modelReturns[i,:])
                    else:
                        PnL=PnL*(1-self.modelReturns[i,:])
                    tradeDays=tradeDays+1
                    if abs(posSize)<abs(self.positionSeries[i]):
                        posSize=self.positionSeries[i]
        if self.positionSeries[-1]!=0 and self.positionSeries[-2]*self.positionSeries[-1]>0:
            # Book the Last Trade
            trade[tradeNum-1,0]=tradeNum  
            trade[tradeNum-1,1]=posSize
            trade[tradeNum-1,2]=tradeDays
            if pos>0:
                PnL=PnL-1
            else:
                PnL=1-PnL
            trade[tradeNum-1,5:]=PnL
            exitIndex=i
            self.tradeEntryExitIndex[tradeNum-1,0:4]=[tradeNum,int(entryIndex),int(exitIndex)]
        #  Trim excess rows of trade
        index= [j for j, x in enumerate(trade[:,0]) if x == 0][0]
        trade=trade[0:index,:]
        self.tradeEntryExitIndex=self.tradeEntryExitIndex[0:index]
        # total PnL for each Trade (across all risk units)
        totalTradePnL=np.sum(trade[:,5:],axis=1).reshape((trade.shape[0],1))
        trade=np.hstack((trade,totalTradePnL))
        # Calc Win Lose Indicator & Running Win Ratio
        winLoseIndicator=np.where(np.array(trade[:,-1])>0,1,0)
        trade[:,3]=winLoseIndicator
      
        for j in range(trade.shape[0]):
           tallyWins=sum(trade[0:j+1,3])
           trade[j,4]=tallyWins/(j+1)
        return trade
    
    def CalcTradeStats(self):
        """Summary Trade Statics"""
        self.numTrades=int(max(self.tradeContainer[:,0]))  # Num of Trades
        self.avgPosition=np.mean(abs(self.tradeContainer[:,1]))  # Avg position held in Trades
        self.avgTradeDuration=np.mean(self.tradeContainer[:,2])  # Avg Trade Duration
        tradeStats=np.zeros((4,self.maxPositionSize+1))
        
        self.winRatio=np.zeros((1,self.maxPositionSize+1))
        self.totalPnL=np.zeros((1,self.maxPositionSize+1))
        self.avgWinPnL=np.zeros((1,self.maxPositionSize+1))
        self.avgPnL=np.zeros((1,self.maxPositionSize+1))
        self.avgLossPnL=np.zeros((1,self.maxPositionSize+1))
        
        # Loop For Calc Trade Stats
        for i in range(self.partition-1,self.partition+self.maxPositionSize):
            winTradesIndex=[j for j, x in enumerate(self.tradeContainer[:,i]) if x >0]  # Index of Winning Trades
            if len(winTradesIndex)==0:  # CORNER SOLUTION: NO WINNING TRADES
                #print 'THERE IS BLACK HOLE'
                winTrades=0  # Generate series of win trades
                self.winRatio[0,i-self.partition+1]=0  # WinRAtio of Each Position and Total Position  
                self.avgWinPnL[0,i-self.partition+1]=0
            else:
                winTrades=self.CalcIndexSeries(self.tradeContainer[:,i],winTradesIndex)  # Generate series of win trades
                self.winRatio[0,i-self.partition+1]=(len(winTrades)+0.0)/self.numTrades  # WinRAtio of Each Position and Total Position  
                self.avgWinPnL[0,i-self.partition+1]=np.mean(winTrades)
            
            self.totalPnL[0,i-self.partition+1]=sum(self.tradeContainer[:,i])
            self.avgPnL[0,i-self.partition+1]=np.mean(self.tradeContainer[:,i])
            
            lossTradesIndex=[j for j, x in enumerate(self.tradeContainer[:,i]) if x <=0]  # Set of Losing Trades
            lossTrades=self.CalcIndexSeries(self.tradeContainer[:,i],lossTradesIndex)
            self.avgLossPnL[0,i-self.partition+1]=np.mean(lossTrades)
        tradeStats[0,:] = self.winRatio
        tradeStats[1,:] = self.avgPnL
        tradeStats[2,:] = self.avgWinPnL
        tradeStats[3,:] = self.avgLossPnL
        
        return tradeStats
    
    def CalcSharpeRatios(self):
        """Calculate Sharpe Ratios"""
        sr=np.zeros((1,self.maxPositionSize))
        for i in range(self.maxPositionSize):
            self.sharpeObj=SharpeRatio(self.aggregateModelReturns[:,i],'daily')
            sr[0,i]=self.sharpeObj.sharpeRatio
        return sr
    
    def CalcDrawdown(self):
        """Calculate DrawDown on accumulateReturns"""
        dd=np.zeros((self.height,self.maxPositionSize))
        
        for i in range(self.maxPositionSize):
            StartLoop=[k for k, x in enumerate(self.accumulatedModelReturns[:,i]) if x >0][0]+1   # find the first +ve trade
            high=self.accumulatedModelReturns[StartLoop,i]  # remembers the last high
            
            for j in range(StartLoop,self.height):
                if self.accumulatedModelReturns[j,i]-high>=0:
                    dd[j,i]=0
                    high=self.accumulatedModelReturns[j,i]
                else:
                    dd[j,i]=-(1-(self.accumulatedModelReturns[j,i]/high))

        self.maxDrawdown=dd.min(0)
        return dd
    
    def CalcIntraTradePnL(self):
        """Calc the Max & Min Intra PnL Within Each Trade"""
        self.intraTradeMaxPnL=np.zeros((self.numTrades,self.maxPositionSize))
        self.intraTradeMinPnL=np.zeros((self.numTrades,self.maxPositionSize))
        #print self.positionSeries
        for i in range(self.numTrades):
            for j in range(self.maxPositionSize):
                entryIndex=self.tradeEntryExitIndex[i,1]  # find the entry Index
                exitIndex=self.tradeEntryExitIndex[i,2]  # find the exit Index 
                trade=self.modelReturns[entryIndex:exitIndex+1,j]  # Capture the trade and its daily returns
                PnL=np.ones(exitIndex-entryIndex)  # set up PnL Container for trade. 
                for k in range(1,len(trade)):  
                    if k==1:
                        PnL[k-1]=1+trade[k]
                    else:
                        PnL[k-1]=(1+trade[k])*PnL[k-2]
                self.intraTradeMinPnL[i,j]=(min(PnL)-1.0)*100
                self.intraTradeMaxPnL[i,j]=(max(PnL)-1.0)*100
        # Turn Unused Risk Units to NaN
        for i in range(self.numTrades):
            posUsed=int(abs(self.tradeContainer[i,1]))
            if posUsed!=self.maxPositionSize:
                self.intraTradeMinPnL[i,posUsed:]=np.nan
                self.intraTradeMaxPnL[i,posUsed:]=np.nan
    
    def CalcIndexSeries(self,series,indexSeries):
        """Calc a new series from an index[] generated from find(.) array"""
        s=series[indexSeries]
        return s
    
    def CheckNan(self,x):
        """check for NaN in price Series"""
        nanSeries=[i for i,each in enumerate(x) if np.isnan(each) ]  # Records the Array Index where there is a NaN 
        for i in range(len(nanSeries)):
            if nanSeries[i]==0:  # If first element =NaN,replace with average  
                x[nanSeries[i]]=np.nanmean(x[:10])
            else:  # Replace NaN with prev value
                x[nanSeries[i]]=x[nanSeries[i]-1]
        return x
 


"""
if __name__ == "__main__":
    data=pd.read_excel("c:\Book1.xlsx",'Sheet5')
    data.set_index("Date",inplace=True)
    pos=data['Signal'].tolist()
    m=int(max(map(abs, pos)))
    t=TradeAnalysis(data,pos,m)
    print t.intraTradeMaxPnL
"""   
  
    
