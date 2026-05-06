import streamlit as st 
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

st.title('Stock Dashboard') 

Ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

if Ticker:
    data = yf.download(Ticker, start=start_date, end=end_date)
    if not data.empty:
        data.columns = data.columns.get_level_values(0)
        fig = px.line(data, x=data.index, y='Close', title=Ticker)
        st.plotly_chart(fig)

    pricing_data, fundamental_data, news = st.tabs(['Pricing Data', 'Fundamental Data', 'News'])

    with pricing_data:
        st.header('Price Movement')
        data2 = data.copy()
        data2['% Change'] = data['Close'] / data['Close'].shift(1) - 1
        data2.dropna(inplace=True)
        st.write(data2)

        annual_return = data2['% Change'].mean() * 252 * 100
        st.write('Annual Return is', round(annual_return, 2), '%')

        stdev = np.std(data2['% Change']) * np.sqrt(252)
        st.write('Standard Deviation is', round(stdev * 100, 2), '%')

        risk_adj_return = annual_return / (stdev * 100)
        st.write('Risk Adjusted Return is', round(risk_adj_return, 2))

    with fundamental_data:
        try:
            key = '3QGG2XI66GJ9I6ND'
            fd = FundamentalData(key, output_format='pandas')

            st.subheader('Balance Sheet')
            balance_sheet = fd.get_balance_sheet_annual(Ticker)[0]
            bs = balance_sheet.T[2:]
            bs.columns = list(balance_sheet.T.iloc[0])
            st.write(bs)

            st.subheader('Income Statement')
            income_statement = fd.get_income_statement_annual(Ticker)[0]
            is1 = income_statement.T[2:]
            is1.columns = list(income_statement.T.iloc[0])
            st.write(is1)

            st.subheader('Cash Flow Statement')
            cash_flow = fd.get_cash_flow_annual(Ticker)[0]
            cf = cash_flow.T[2:]
            cf.columns = list(cash_flow.T.iloc[0])
            st.write(cf)

        except ValueError as e:
            st.warning('Alpha Vantage API rate limit reached (25 requests/day). Please try again tomorrow or upgrade your plan.')

    with news:
        st.header(f'News about {Ticker}')
        sn = StockNews(Ticker, save_news=False)
        df_news = sn.read_rss()
        for i in range(10):
            st.subheader(f'News {i+1}')
            st.write(df_news['published'][i])
            st.write(df_news['title'][i])
            st.write(df_news['summary'][i])
            st.write(f'Title Sentiment: {df_news["sentiment_title"][i]}')
            st.write(f'News Sentiment: {df_news["sentiment_summary"][i]}')
