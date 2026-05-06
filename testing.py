import streamlit as st 
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

# Title of dashboard
st.title('stock dashboard') 

# Adding sidebar for Ticker , Start date and End date
Ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('start date')
end_date = st.sidebar.date_input('end date')

if Ticker:
    data = yf.download(Ticker, start=start_date, end=end_date)

    if not data.empty:
        # Fix MultiIndex columns from yfinance
        data.columns = data.columns.get_level_values(0)

        fig = px.line(data, x=data.index, y='Close', title=Ticker)
        st.plotly_chart(fig)

# Creating 3 new tabs 
pricing_data, fundamental_data, news = st.tabs(['pricing data', 'fundamental data', 'news'])

# Mentioning the details in the pricing data tab
with pricing_data:
    st.header('price Movement')
    data2 = data
    data2['% Change'] = data['Close'].squeeze() / data['Close'].squeeze().shift(1) - 1 # Adding an extra coloumn for % change
    data2.dropna(inplace = True) # Dropped null values
    st.write(data2)

# Calculating annual return
    annual_return = data2['% Change'].mean()*252*100 # Multiplied the mean return with *252(working days) to get annual return
    st.write('Annual return is', annual_return, '%' )
    
# Calculating standard deviation
    stdev = np.std(data2['% Change'])*np.sqrt(252) 
    st.write('standard deviation is', stdev*100, '%')
    st.write('risk adjusted return is', annual_return/(stdev*100,))

# Importing alpha vantage api to get fundamental data of stocks
    from alpha_vantage.fundamentaldata import FundamentalData
    with fundamental_data:
        key = '3QGG2XI66GJ9I6ND' 
        fd = FundamentalData(key, output_format = 'pandas')
        st.subheader('Balance sheet')
        balance_sheet = fd.get_balance_sheet_annual(Ticker)[0]
        bs = balance_sheet.T[2:] # Used transpose for better data visualisation
        bs.columns = list(balance_sheet.T.iloc[0]) 
        st.write(bs)

        st.subheader('income statement')
        income_statement = fd.get_income_statement_annual(Ticker)[0]
        is1 = income_statement.T[2:] # Used transpose for better data visualisation
        is1.columns = list(income_statement.T.iloc[0])
        st.write(is1)

        st.subheader('Cash Flow Statement')
        cash_flow = fd.get_cash_flow_annual(Ticker)[0]
        cf = cash_flow.T[2:] # Used transpose for better data visualisation
        cf.columns = list(cash_flow.T.iloc[0])
        st.write(cf) 

# Installed stocknews liabrary and using the API to get news of the stock
from stocknews import StockNews
with news:
    st.header(f'News about {Ticker}')
    sn = StockNews(Ticker, save_news = False) # We dont want to save the news (used false)
    df_news = sn.read_rss() # Creates a dataframe of recent news
    for i in range(10): # We need top 10 News
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i]) # Publised Date
        st.write(df_news['title'][i]) # Title of news
        st.write(df_news['summary'][i]) # Summary of news
        title_sentiment = df_news['sentiment_title'][i] # Sentiment of title
        st.write(f'Title Sentiment {title_sentiment}')
        news_sentiment = df_news['sentiment_summary'][i] # Sentiment of summary
        st.write(f'News Sentiment {news_sentiment}')   

        



