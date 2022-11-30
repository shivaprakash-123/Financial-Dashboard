import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
from monteCarlo import MonteCarlo
import matplotlib.pyplot as plt
import numpy as np


# Backend
def load_companies_names(fle):
    '''this loads companies list'''
    ticker_list = pd.read_html(fle)[0]['Symbol']
    return ticker_list

def get_ticker_data(stock_name):
    '''this gets stock data from stock name'''
    stock = yf.Ticker(stock_name)
    return stock


# fucntion to get  values required to show in summary page

def get_stock_summary(stock):
    
    stock_info = stock.info
    # passing all required values to dictionry
    summaries1 = { "days_range": str(stock_info['dayLow']) + " - " + str(stock_info['dayHigh']) , \
                  '52 week range' :  str(stock_info['fiftyTwoWeekLow']) + " - " + str(stock_info['fiftyTwoWeekHigh']),\
                      'Previous Close': stock_info['previousClose'],'Ask':stock_info['ask'],'Bid':stock_info['bid'],\
                          'Open':stock_info['open'], "Volume": stock_info['volume'], \
                              "Average Volume": stock_info['averageVolume']  }
    df1 = pd.DataFrame(list(summaries1.items()))
   # passing all required values to dictionry
    summaries2 = {"Market Cap":stock_info["marketCap"],"Beta":stock_info["beta"], \
                  "PE Ratio":stock_info["trailingPE"], "EPS":stock_info["trailingEps"],\
                  "Forward Dividends & Yield": stock_info["dividendYield"], \
                      'exDividendDate : ' :  stock_info['exDividendDate'],\
                          "1y Target Est.":stock_info["targetMedianPrice"]}
        #converting it into dataframe
        
    df2 = pd.DataFrame(list(summaries2.items()))
    print(df1,df2)
    
    return (df1,df2)


# function to get stock history
def get_history(stock, date_range):
    hist = stock.history(period=date_range)
    #print(hist)
    return hist

# Vfunction to get montecarle simualtion
def plot_simulation_price(mc_sim):
    # Plot the simulation stock price in the future
    fig, ax = plt.subplots()
    fig.set_size_inches(15, 10, forward=True)

    plt.plot(mc_sim.simulation_df)
    plt.title('Monte Carlo simulation for ' + mc_sim.ticker + \
                  ' stock price in next ' + str(mc_sim.time_horizon) + ' days')
    plt.xlabel('Day')
    plt.ylabel('Price')

    plt.axhline(y=mc_sim.stock_price['Close'][-1], color='red')
    plt.legend(['Current stock price is: ' + str(np.round(mc_sim.stock_price['Close'][-1], 2))])
    ax.get_legend().legendHandles[0].set_color('red')

    return fig
# creating required tabs
def create_tabs():
    tabs = ['Summary','Chart', 'Financials', 'MonteCarlo', 'Misc']
    return st.tabs(tabs)

# defining main function which hold all subfunctions
def main_page():
    companies = load_companies_names('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    main_container = st.container()
    # creating a container
    with main_container:
        header_container = st.container()
        with header_container:
            print("In header Container")
            
            stock_selected = st.selectbox("Companies List",companies)
            # using the session state to acees  stock
            if 'stock_selected' not in st.session_state:
                    st.session_state['stock_selected'] = stock_selected
            btn = st.button("Get Data", key="get")
            with st.container():
                tab1,tab2,tab3,tab4,tab5 = create_tabs()
        # creating required date range and btn for the tab 2 -chart
            with tab2:
                with st.container():
                    date_range = st.selectbox("Date Range",["1m","3m","6m","ytd", "1y", "3y", "5y", "max"])
                    btnrange = st.button("history", key="loadChart")

            if btn:
                if 'stock_selected' not in st.session_state:
                    st.session_state['stock_selected'] = stock_selected
                elif st.session_state.stock_selected != stock_selected:
                    st.session_state['stock_selected'] = stock_selected
                    
           # creating the columns in tab1 and writing the values to it 
            with tab1:
                if not st.session_state.stock_selected:
                    st.write("No Stock Selected")
                with st.container():
                    col1, col2 = st.columns(2)
                    stock = get_ticker_data(stock_selected)
                    c1,c2 = get_stock_summary(stock)
                    col1.write(c1)
                    col2.write(c2)
 #creating the required time range  and options to slect financail sheets
            with tab3:
                financial = st.selectbox("Financial",["Income Statement", "Balance Sheet", "Cash Flow"])
                time_range = st.selectbox("Time Range",["Annual", "Quarterly"])
                btnfinancial = st.button("financial", key="financial")
#  creatinf the  selectbox to select the number of simulation
            with tab4:
                stock_selected = st.session_state.stock_selected
                n_simulation = st.selectbox("N Simulation",[200, 500, 1000])
                time_horizon = st.selectbox("Time Horizon",[30, 60, 90])

                start_date = str(dt.date.today().isoformat())
                end_date = str((dt.datetime.now() + dt.timedelta(days=time_horizon)).date().isoformat())
                btnsimulate = st.button("Simulate", key="simulate")
                print("n_simulation", n_simulation)
                print("time_horizon", time_horizon)
                print("start_date", start_date)
                print("end_date", end_date)
                
                
                if btnsimulate:
                    mc_sim = MonteCarlo(ticker=stock_selected, data_source='yahoo', start_date="2021-01-01", end_date="2022-11-30", time_horizon=time_horizon, n_simulation=n_simulation, seed=123)
                    simulation_df = mc_sim.run_simulation()
                    print(simulation_df)
                    with st.container():
                        st.pyplot(plot_simulation_price(mc_sim))
   # tab to add additional info of the companies
            with tab5:
                if not st.session_state.stock_selected:
                    st.write("No Stock Selected")
                if not stock:
                        stock = get_ticker_data(st.session_state.stock_selected)
            # adding stock news data to the tab 5
                stock_news = stock.news#json.load(stock.news)
                #print(stock_news)
                if len(stock_news) > 0:
                    for i in range(len(stock_news)):
                        st.write(stock_news[i]["title"])
                        st.write(stock_news[i]["link"])
                else:
                    st.write("No News Found")


     
            if btnrange:
                if not st.session_state.stock_selected:
                    st.write("No Stock Selected")
                with st.container():
                    if not stock:
                        stock = get_ticker_data(st.session_state.stock_selected)

                    hist_data = get_history(stock,date_range)
                    st.line_chart(hist_data)
            # writing the required values to financial tab
            if btnfinancial:
                if not st.session_state.stock_selected:
                    st.write("No Stock Selected")
                with st.container():
                    if not stock:
                        stock = get_ticker_data(st.session_state.stock_selected)
                    if not financial:
                        financial = "Income Statement"
                    if not time_range:
                        time_range = "Annual"

                    if financial == "Income Statement" and time_range == "Annual":
                        st.write(stock.earnings)
                    elif financial == "Income Statement" and time_range == "Quarterly":
                        st.write(stock.quarterly_earnings)
                    elif financial == "Balance Sheet" and time_range == "Annual":
                        st.write(stock.balance_sheet)
                    elif financial == "Balance Sheet" and time_range == "Quarterly":
                        st.write(stock.quarterly_balance_sheet)
                    elif financial == "Cash Flow" and time_range == "Annual":
                        st.write(stock.cashflow)
                    elif financial == "Cash Flow" and time_range == "Quarterly":
                        st.write(stock.quarterly_cashflow)
# calling functions
if __name__ == '__main__':
   # writing the title 
    st.title("My simple financial dashboard")
    st.write("Data source: Yahoo Finance")
    # st.title("Streamlit Tutorial App")
    # st.write("This is my new app")
    main_page()

    # https://discuss.streamlit.io/t/case-of-disappearing-interactive-widget/1069 - issue with multiple buttons
