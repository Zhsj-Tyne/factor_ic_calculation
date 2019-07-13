from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as st
import statsmodels.api as sm


class IC_Analyzer(object):

    def __init__(self, stock_tab):
        self.__stock_tab = stock_tab

    def get_EP(self):
        print('a')
        self.__stock_tab['EP'] = self.__stock_tab['pe_ttm'].map(lambda x:1.0/x)
        return self.__stock_tab

    def get_BP(self):
        print('b')
        self.__stock_tab['BP'] = self.__stock_tab['pb_lf'].map(lambda x: 1.0 / x)
        return self.__stock_tab

    def get_SP(self):
        print('c')
        self.__stock_tab['SP'] = self.__stock_tab['ps_ttm'].map(lambda x: 1.0 / x)
        return self.__stock_tab

    def get_default(self):
        return('Please input correct format!')

    def factor(self):
        factor = input("Please input single factor you want for IC factors evaluation and test: EP/BP/SP\n")
        switcher = {
            "EP": self.get_EP,
            "BP": self.get_BP,
            "SP": self.get_SP,
            "default": self.get_default
        }
        factor_cfm = switcher.get(factor,self.get_default)()
        print('Single factor chosen is '+ factor)
        return factor_cfm,factor

    def factor_ic_calculation(self,factor):
        self.__stock_tab['return'] = self.__stock_tab['nxt_close'] / self.__stock_tab['close'] - 1
        print(np.cov(self.__stock_tab['return'],self.__stock_tab[factor])[0][1])
        # print(self.__stock_tab['return'])


    def tidy_tab(self,factor):
        self.deal_extreme(factor)
        self.zscore(factor)
        self.fill_nan()
        new_col = self.neutralize(factor)
        return self.__stock_tab,new_col

    def deal_extreme(self,col_name,threshold_up = 5,threshold_dwn = -5):
        # self.__stock_tab = self.__stock_tab.sort_values(by = col_name)

        self.__stock_tab['difference'] = self.__stock_tab[col_name].map(lambda x: abs(x-self.__stock_tab[col_name].median()))
        median_difference = self.__stock_tab['difference'].median()
        if median_difference == 0:
            s = 0
        else:
            self.__stock_tab['mask'] = self.__stock_tab['difference'].map(lambda x: x/float(median_difference))
        self.__stock_tab.loc[self.__stock_tab['mask'] > threshold_up,col_name] = 5
        self.__stock_tab.loc[self.__stock_tab['mask'] < threshold_dwn, col_name] = -5
        #print("deal extreme", self.__stock_tab)
        print("aaa",self.__stock_tab[[col_name,'mask','difference']])


    def zscore(self,col_name):
        std_var = self.__stock_tab[col_name].std()
        mean = self.__stock_tab[col_name].mean()
        dealt_name = 'zscore_' + col_name
        self.__stock_tab[dealt_name] = self.__stock_tab[col_name].map(lambda x: (x-mean)/float(std_var))
        print("zscore", self.__stock_tab)
        print("aaa",self.__stock_tab[[col_name,'mask','difference',dealt_name]])#??????????/


    def fill_nan(self):
        # self.__stock_tab[col_name]=self.__stock_tab[col_name].fillna(value = 0)
        self.__stock_tab = self.__stock_tab.fillna(value=0)


    def neutralize(self,col_name):
        # Wind中在计算PB、PE等估值因子时，是以总市值2(mkt_cap_ard)为依据的，
        # 去除市值、行业因素，得到新的因子值
        based_on = 'log_mkt_cap_ard'
        print(self.__stock_tab.columns)
        industry = self.__stock_tab.iloc[:,48:-4]
        # industry.drop(['Unnamed: 57'], axis=1, inplace=True)
        unnamed_index = list(industry.columns.str.contains('Unnamed')).index(True)
        industry.drop([industry.columns[unnamed_index]], axis=1, inplace=True)
        print(industry.columns)
        y = self.__stock_tab.iloc[:, -1]
        x = self.__stock_tab[based_on]
        x = np.column_stack((x, industry))
        x = sm.add_constant(x)

        est = sm.OLS(y, x).fit()
        new_col = 'res_'+col_name
        self.__stock_tab[new_col] = est.resid
        print(est.summary())
        return new_col

        # fig, ax = plt.subplots(figsize=(8, 6))
        # ax.plot(x, y, 'o', label="data")
        # ax.plot(x, est.fittedvalues, 'r--.', label="OLS")
        # ax.legend(loc='best')
        # plt.show()
        # print(self.__stock_tab)
