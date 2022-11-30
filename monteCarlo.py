import datetime as dt
from matplotlib import pyplot as plt
import pandas as pd
from pandas_datareader import data as web
import numpy as np

class MonteCarlo(object):
    
    def __init__(self, ticker, data_source, start_date, end_date, time_horizon, n_simulation, seed):
        
        # Initiate class variables
        self.ticker = ticker  # Stock ticker
        self.data_source = data_source  # Source of data, e.g. 'yahoo'
        self.start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')  # Text, YYYY-MM-DD
        self.end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')  # Text, YYYY-MM-DD
        self.time_horizon = time_horizon  # Days
        self.n_simulation = n_simulation  # Number of simulations
        self.seed = seed  # Random seed
        self.simulation_df = pd.DataFrame()  # Table of results
        
        # Extract stock data
        self.stock_price = web.DataReader(ticker, data_source, self.start_date)
        print(self.stock_price)

        
        # Calculate financial metrics
        # Daily return (of close price)['Adj Close']
        self.daily_return = self.stock_price['Close'].pct_change()

        # Volatility (of close price)
        self.daily_volatility = np.std(self.daily_return)
        print("Created object")
        
    def run_simulation(self):
        
        # Run the simulation
        np.random.seed(self.seed)
        self.simulation_df = pd.DataFrame()  # Reset
        print(self.ticker, self.time_horizon,self.start_date,self.end_date)
        print(self.stock_price['Close'][-1])
        print("Daily Return\n",self.daily_return)
        
        for i in range(self.n_simulation):

            # The list to store the next stock price
            next_price = []

            # Create the next stock price
            last_price = self.stock_price['Close'][-1]

            for j in range(self.time_horizon):
                
                # Generate the random percentage change around the mean (0) and std (daily_volatility)
                future_return = np.random.normal(0, self.daily_volatility)

                # Generate the random future price
                future_price = last_price * (1 + future_return)

                # Save the price and go next
                next_price.append(future_price)
                last_price = future_price

            # Store the result of the simulation
            next_price_df = pd.Series(next_price).rename('sim' + str(i))
            self.simulation_df = pd.concat([self.simulation_df, next_price_df], axis=1)
        print(self.simulation_df)
        return self.simulation_df

    def plot_simulation_price(self):
        
        # Plot the simulation stock price in the future
        fig, ax = plt.subplots()
        fig.set_size_inches(15, 10, forward=True)

        plt.plot(self.simulation_df)
        plt.title('Monte Carlo simulation for ' + self.ticker + \
                  ' stock price in next ' + str(self.time_horizon) + ' days')
        plt.xlabel('Day')
        plt.ylabel('Price')

        plt.axhline(y=self.stock_price['Close'][-1], color='red')
        plt.legend(['Current stock price is: ' + str(np.round(self.stock_price['Close'][-1], 2))])
        ax.get_legend().legendHandles[0].set_color('red')

        plt.show()
    
    def plot_simulation_hist(self):
        
        # Get the ending price of the 200th day
        ending_price = self.simulation_df.iloc[-1:, :].values[0, ]

        # Plot using histogram
        fig, ax = plt.subplots()
        plt.hist(ending_price, bins=50)
        plt.axvline(x=self.stock_price['Close'][-1], color='red')
        plt.legend(['Current stock price is: ' + str(np.round(self.stock_price['Close'][-1], 2))])
        ax.get_legend().legendHandles[0].set_color('red')
        plt.show()
    
    def value_at_risk(self):
        # Price at 95% confidence interval
        future_price_95ci = np.percentile(self.simulation_df.iloc[-1:, :].values[0, ], 5)

        # Value at Risk
        VaR = self.stock_price['Close'][-1] - future_price_95ci
        print('VaR at 95% confidence interval is: ' + str(np.round(VaR, 2)) + ' USD')
        return VaR
		
		


if __name__=='__main__':
    stock_selected = 'AAPL'
    n_simulation = 500
    time_horizon = 30
    start_date = str(dt.date.today().isoformat())
    end_date = str((dt.datetime.now() + dt.timedelta(days=time_horizon)).date().isoformat())

	# Initiate
    #mc_sim = MonteCarlo(ticker='AAPL', data_source='yahoo',start_date='2020-01-01', end_date='2020-11-04',time_horizon=30, n_simulation=1000, seed=123)
    mc_sim = MonteCarlo(ticker=stock_selected, data_source='yahoo', start_date=start_date, end_date=end_date, time_horizon=time_horizon, n_simulation=n_simulation, seed=123)
    # Print out data
    mc_sim.stock_price.tail()
    # Run simulation
    mc_sim.run_simulation()
    #Plot the results
    #mc_sim.plot_simulation_price()
