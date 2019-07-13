# coding=utf-8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from WindPy import *
import datetime,time
import os
import sys
import ic_calculation
# import index

class Stockset(object):

    def __init__(self, price='close', fq='post',industry='jq_l1', weight_method='avg'):
        self.__price = price
        self.__industry = industry
        self.__weight_method = weight_method
        self.__begin = '2009-1-23'
        self.__terminal = '2016-8-31'

    def initialize(self):
        self.__begin = datetime.datetime.strptime(self.__begin,'%Y-%m-%d')
        self.__terminal = datetime.datetime.strptime(self.__terminal,'%Y-%m-%d')
        print('Backward time interval is between %s and %s' % (self.__begin,self.__terminal))
        print("Please input time point you want for IC factors evaluation and test: ")
        timepoint = datetime.datetime.strptime(input("Target Day: "),'%Y-%m-%d')
        w.start()
        jiaoyi_day = w.tdays(self.__begin, self.__terminal, "")
        if((timepoint >= self.__begin) & (timepoint <=self.__terminal)):
            if timepoint in jiaoyi_day.Times:
                pass
            else:
                timepoint = w.tdaysoffset(-1, timepoint, "")
                print("Your timepoint is not a transaction day, 1 day offset behind chosen day:",timepoint.Times)
        else:
            raise ValueError('Wrong input!')
        timepoint = self.datetime_2_str(timepoint)
        return timepoint

    def datetime_2_str(self,crossed_day):
        crossed_day = crossed_day.Data[0][0]
        crossed_day = crossed_day.strftime('%Y-%m-%d')
        return crossed_day

    def excluding_stock(self, crossed_day,stock_symbols):
        # 停牌和涨停股票信息
        nxt_crossed_day = w.tdaysoffset(1, crossed_day, "")
        nxt_crossed_day = self.datetime_2_str(nxt_crossed_day)
        #停牌股票
        suspend_stocks = w.wset("TradeSuspend",
               "startdate = " + nxt_crossed_day + " ;enddate=" + nxt_crossed_day +";field=wind_code,sec_name,suspend_type,suspend_reason")
        suspend_code = list(pd.Series(suspend_stocks.Data[0]))

        #涨停股票
        peak_stocks = w.wset("TradeSuspend",
                                "startdate = " + nxt_crossed_day + " ;enddate=" + nxt_crossed_day + ";field=wind_code,sec_name,suspend_type,suspend_reason")
        peak_code = list(pd.Series(peak_stocks.Data[0]))#modificate

        # 取ST股票等风险警示股票信息
        st_stocks = w.wset("SectorConstituent", u"date=" + crossed_day + ";sector=风险警示股票;field=wind_code,sec_name")
        st_code = list(pd.Series(st_stocks.Data[0]))

        excluding_stocks = set(suspend_code).union(set(st_code)).union(set(peak_code))
        excluded_stocks = list(set(stock_symbols).difference(excluding_stocks))
        #print("excluding_stocks:",excluding_stocks)
        return excluded_stocks

    def integrate_stock_value(self,stock_code, crossed_day):
        merge_row=pd.DataFrame()
        i = 0
        for stock in stock_code:
            print("stock",stock,type(stock))
            single_row = self.get_single_stock(stock,crossed_day)
            # merge_row = merge_row.append(single_row)
            merge_row = pd.concat([merge_row, single_row],axis = 0, sort =  False)
            # print(merge_row)
            # i = i+1
            # if i>4:
            #     break
            # # print(merge_data)
        return merge_row

    def get_single_stock(self, stock_code, crossed_day):
        index_data=pd.DataFrame()
        #w.start()
        stock = w.wsd(stock_code,
                  "trade_code,open,high,low,close,pre_close,volume,amt,dealnum,chg,pct_chg,vwap, adjfactor,close2,turn,free_turn,oi,oi_chg,pre_settle,settle,chg_settlement,pct_chg_settlement, lastradeday_s,last_trade_day,rel_ipo_chg,rel_ipo_pct_chg,susp_reason,close3, pe_ttm,val_pe_deducted_ttm,pe_lyr,pb_lf,ps_ttm,ps_lyr,dividendyield2,ev,mkt_cap_ard,pb_mrq,pcf_ocf_ttm,pcf_ncf_ttm,pcf_ocflyr,pcf_nflyr",
                  crossed_day,crossed_day)
        #print(stock)
        # print(type(stock))
        nxt_crossed_day = w.tdaysoffset(1, crossed_day, "")
        nxt_crossed_day = self.datetime_2_str(nxt_crossed_day)
        stock_nxt_d = w.wsd(stock_code,"trade_code,close",nxt_crossed_day,nxt_crossed_day)
        industry = w.wss(stock_code, "abs_industry").Data[0][0]
        print(industry)
        index_data['trade_date'] = stock.Times
        index_data['stock_code'] = stock_code
        print(stock.Data[0])
        index_data['open'] = stock.Data[1]
        index_data['high'] = stock.Data[2]
        index_data['low'] = stock.Data[3]
        index_data['close'] = stock.Data[4]
        index_data['pre_close'] = stock.Data[5]
        index_data['volume'] = stock.Data[6]
        index_data['amt'] = stock.Data[7]
        index_data['dealnum'] = stock.Data[8]
        index_data['chg'] = stock.Data[9]
        index_data['pct_chg'] = stock.Data[10]
        # index_data['pct_chg']=index_data['pct_chg']/100
        index_data['vwap'] = stock.Data[11]
        index_data['adj_factor'] = stock.Data[12]
        index_data['close2'] = stock.Data[13]
        index_data['turn'] = stock.Data[14]
        index_data['free_turn'] = stock.Data[15]
        index_data['oi'] = stock.Data[16]
        index_data['oi_chg'] = stock.Data[17]
        index_data['pre_settle'] = stock.Data[18]
        index_data['settle'] = stock.Data[19]
        index_data['chg_settlement'] = stock.Data[20]
        index_data['pct_chg_settlement'] = stock.Data[21]
        index_data['lastradeday_s'] = stock.Data[22]
        index_data['last_trade_day'] = stock.Data[23]
        index_data['rel_ipo_chg'] = stock.Data[24]
        index_data['rel_ipo_pct_chg'] = stock.Data[25]
        index_data['susp_reason'] = stock.Data[26]
        index_data['close3'] = stock.Data[27]
        index_data['pe_ttm'] = stock.Data[28]
        index_data['val_pe_deducted_ttm'] = stock.Data[29]
        index_data['pe_lyr'] = stock.Data[30]
        index_data['pb_lf'] = stock.Data[31]
        index_data['ps_ttm'] = stock.Data[32]
        index_data['ps_lyr'] = stock.Data[33]
        index_data['dividendyield2'] = stock.Data[34]
        index_data['ev'] = stock.Data[35]
        index_data['mkt_cap_ard'] = stock.Data[36]
        index_data['pb_mrq'] = stock.Data[37]
        index_data['pcf_ocf_ttm'] = stock.Data[38]
        index_data['pcf_ncf_ttm'] = stock.Data[39]
        index_data['pcf_ocflyr'] = stock.Data[40]
        index_data['pcf_ncflyr'] = stock.Data[41]
        index_data['log_mkt_cap_ard'] = np.log(stock.Data[36])
        index_data['nxt_close'] = stock_nxt_d.Data[1]
        index_data['data_source'] = 'Wind'
        index_data['created_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        index_data['updated_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #get dummy industry variable
        index_data[industry] = 1
        index_data = index_data.loc[index_data['open'] > 0]
        #print(index_data)
        return index_data

    def constituent_list(self,crossed_day):
        w.start()
        constituent_code = w.wset("sectorconstituent", "date = " + crossed_day + "; windcode = 000906.SH; field = wind_code,sec_name")
        print(list(pd.Series(constituent_code.Data[0])))# focus
        return constituent_code.Data[0] #print(list(pd.Series(constituent_code.Data[0])))

def main():
    # reprocess
    windStock = Stockset()
    time_selected= windStock.initialize()
    # stock_symbols = windStock.constituent_list(time_selected)
    # stock_symbols = windStock.excluding_stock(time_selected,stock_symbols)
    # cleaned_stock_tab = windStock.integrate_stock_value(stock_symbols, time_selected)
    # cleaned_stock_tab.to_csv("E:\output\consitituents_other.csv", index=False)
    # print("finished")

    cleaned_stock_tab = pd.read_csv("E:\output\consitituents_other.csv", encoding = "utf-8")
    print(cleaned_stock_tab)
    ic_analyzer = ic_calculation.IC_Analyzer(cleaned_stock_tab)
    factor_tab,factor_selected = ic_analyzer.factor()
    tidy_factor_tab, factor_col = ic_analyzer.tidy_tab(factor_selected)
    print(factor_selected,'IC value in ',time_selected, ':\n')
    ic_analyzer.factor_ic_calculation(factor_col)
    #factor exposure



    #
    # daily_cstuen.to_csv("E:\output\consitituents.csv", index=False)
    #
    # print(cross_day, 'Finished')

if __name__ == "__main__":
    main()