# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 16:30:27 2017
    % Analysis of a portfolio of trades. Includes:
    % i) Sharpe
    % ii) DrawDown
    % iii) Max/Min Return
    % iv) Annualized Return 
@author: luoying.li
"""
from SharpeRatio import SharpeRatio
from DrawDown import DrawDown



class PortfolioAnalysis:
    def __init__(self,portfolioReturns):
        """ Constructor"""
        self.portfolioReturns=portfolioReturns
        self.totalReturn=portfolioReturns[-1]-1
        self.annualizedReturn=PortfolioAnalysis.CalcAnnualizedRet(portfolioReturns)
        self.maxReturn=max(self.portfolioReturns)-1
        self.minReturn=min(self.portfolioReturns)-1
        
        self.drawDownObj=DrawDown(self.portfolioReturns)
        self.drawDownSeries=self.drawDownObj.drawDownSeries
        self.maxDrawDown=self.drawDownObj.maxDrawDown
        
        self.sharpeObj=SharpeRatio(self.portfolioReturns,'daily','cumulRet')
        self.sharpeRatio=self.sharpeObj.sharpeRatio
    
    @staticmethod 
    def CalcAnnualizedRet(ret):
        """calculateAnnualizedReturn"""
        yr=252
        numofYrs=(len(ret)+0.0)/yr
        finalRet=ret[-1]
        annRet=(finalRet)**(1.0/numofYrs)-1
        return annRet
    
    