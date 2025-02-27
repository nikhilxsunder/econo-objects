"""
econo-objects: A simple python package for creating economic models and data objects using FRED API data.
"""
import os
from fedfred import FredAPI
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame
import numpy as np
from scipy.stats import zscore

class Keys:
    """
    Keys class for managing API key.
    Uses a class variable to store the key so all instances share the same API key.
    """
    _fred_api_key = None
    @classmethod
    def set_fred_api_key(cls, api_key):
        """Sets the FRED API key globally."""
        cls._fred_api_key = api_key
    @classmethod
    def get_fred_api_key(cls):
        """Retrieves the stored FRED API key or falls back to environment variable."""
        if cls._fred_api_key is None:
            cls._fred_api_key = os.getenv("FRED_API_KEY", "")
        if not cls._fred_api_key:
            raise ValueError("FRED API key is not set! Use Keys.set_fred_api_key('your_api_key')")
        return cls._fred_api_key

class FredObject:
    """
    Data Object for Fred Series.
    """
    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.fred_api = FredAPI(Keys.get_fred_api_key())
        self.data = self.fred_api.get_series_observation(self.symbol, observation_start=start_date, observation_end=end_date)
        self.series_info = self.fred_api.get_series(self.symbol)
    def __repr__(self):
        return f'FredObject({self.symbol}, {self.start_date}, {self.end_date})'
    def __get_title(self):
        title = self.series_info['seriess'][0]['title']
        return title
    def to_df(self):
        """
        Converts the data to a DataFrame.
        """
        df = pd.DataFrame(self.data['observations'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df['value'] = pd.to_numeric(df['value'], errors = 'coerce')
        return df.dropna().ffill()
    def plot_df(self, width=10, height=6):
        """
        Plots the data from the DataFrame.
        """
        df = self.to_df()
        df['value'].plot(title=self.__get_title, figsize=(width, height))
        plt.xlabel('Date')
        plt.ylabel('Value')
        return plt.show()

class TimeSeriesAnalysisObject:
    """
    Data Object for Time Series Analysis
    """
    def __init__(self, target, start_date=None, end_date=None):
        self.start_date = start_date
        self.end_date = end_date
        self.target = target
        if isinstance(target, str):
            if not start_date or not end_date:
                raise ValueError("Start date and end date must be provided if the target is a symbol string.")
            self.data = FredObject(target, start_date, end_date).to_df()
        elif isinstance(target, DataFrame):
            if start_date or end_date:
                raise ValueError("Start date and end date should not be provided if the target is a DataFrame.")
            self.data = target
        else:
            raise TypeError("Target must either by string symbol or a Pandas DataFrame")
        if "value" not in self.data.columns:
            raise ValueError("DataFrame does not have a value columnn")
    def __repr__(self):
        return f"TimeSeriesAnalysisObject(target={self.target}, start_date={self.start_date}, end_date={self.end_date})"
    def change_rate(self):
        """
        Calculates the change rate of the target series
        """
        df = self.data
        df['change-rate'] = df['value'].pct_change() * 100
        del df['value']
        df = df.rename(columns={'change-rate': 'value'})
        return df
    def differential_change(self):
        """
        Calculates the incremental change of the target series
        """
        df = self.data
        df['change'] = df['value'].diff()
        del df['value']
        df = df.rename(columns={'change': 'value'})
        return df
    def rolling_mean(self, window):
        """
        Calculates a rolling mean for given window of n periods
        """
        df = self.data
        df['rolling-mean'] = df['value'].rolling(window=window).mean()
        del df['value']
        df = df.rename(columns={'rolling-mean': 'value'})
        return df
    def rolling_stdev(self, window):
        """
        Calculates a rolling standard deviation for given window of n periods
        """
        df = self.data
        df['rolling-stdev'] = df['value'].rolling(window=window).std()
        del df['value']
        df = df.rename(columns={'rolling-stdev': 'value'})
        return df
    def log_returns(self, shift=1):
        """
        Calculates logarithmic returns for a given shift of n periods
        """
        df = self.data
        df['log-returns'] = np.log(df['value'] / df['value'].shift(shift))
        del df['value']
        df = df.rename(columns={'log-returns': 'value'})
        return df
    def autocorrelation(self, lag):
        """
        Calculates autocorrelation for a given lag of n periods
        """
        df = self.data
        df['autocorrelation'] = df['value'].autocorr(lag=lag)
        del df['value']
        df = df.rename(columns={'autocorrelation: value'})
        return df

class CurrencyPairObject:
    """
    Data Object for Currency Pair Series.
    """
    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = FredObject(symbol, start_date, end_date).to_df()
    def __repr__(self):
        return f'CurrencyPairObject({self.symbol}, {self.start_date}, {self.end_date})'
    def __get_title(self, symbol):
        title = FredObject(symbol, self.start_date, self.end_date).series_info['seriess'][0]['title']
        return title
    def to_reciprocal_df(self):
        """
        Converts the data to its reciprocal exchange rate.
        """
        df = self.data
        df['reciprocal'] = 1 / df['value']
        del df['value']
        df.rename(columns={'reciprocal': 'value'}, inplace=True)
        return df.dropna().ffill()
    def to_conversion_df(self, conversion_pair, reciprocal_conversion=False):
        """
        Converts the data to a DataFrame with the conversion rate applied.

        the reciprocal_conversion parameter is used to determine if the conversion rate should be 
        applied to the reciprocal of the exchange rate.
        """
        if reciprocal_conversion:
            exchange_df = self.to_reciprocal_df()
        else:
            exchange_df = self.data
        conversion_df = FredObject(conversion_pair, self.start_date, self.end_date).to_df()
        new_pair_df = conversion_df[['value']].rename(columns={'value': conversion_pair}).merge(
            exchange_df[['value']], left_index=True, right_index=True, how='inner'
        )
        new_pair_df['value'] = new_pair_df[conversion_pair] * new_pair_df['value']
        del new_pair_df[conversion_pair]
        return new_pair_df.dropna().ffill()
    def plot_df(self, df_type, conversion_pair=None, width=10, height=6):
        """
        Plots the data from the DataFrame.
        """
        parts = self.__get_title(self.symbol).split()
        quote = " ".join(parts[:2])
        to = parts[2]
        base = " ".join(parts[3:5])
        label = " ".join(parts[5:])
        if conversion_pair:
            parts_c = self.__get_title(conversion_pair).split()
        else:
            parts_c = []
        quote_c = " ".join(parts_c[:2])
        base_c = " ".join(parts_c[3:5])
        if df_type not in {'exchange', 'reciprocal', 'conversion', 'reciprocal_conversion'}:
            raise ValueError('df_type must be either exchange, reciprocal, conversion, or reciprocal_conversion')
        elif df_type == 'exchange':
            self.data['value'].plot(title=f'{quote} {to} {base} {label}', figsize=(width, height))
        elif df_type == 'reciprocal':
            self.to_reciprocal_df()['value'].plot(title=f'{base} {to} {quote} {label}', figsize=(width, height))
        elif df_type == 'conversion':
            if conversion_pair is None:
                raise ValueError('conversion_pair must be provided for conversion df_type')
            else:
                self.to_conversion_df(conversion_pair)['value'].plot(title=f'{quote} {to} {base_c} {label}', figsize=(width, height))
        elif df_type == 'reciprocal_conversion':
            if conversion_pair is None:
                raise ValueError('conversion_pair must be provided for conversion df_type')
            else:
                self.to_conversion_df(conversion_pair, reciprocal_conversion=True)['value'].plot(title=f'{quote_c} {to} {base} {label}', figsize=(width, height))
        plt.xlabel('Date')
        plt.ylabel('Value')
        return plt.show()

class YieldSpreadObject:
    """
    Data Object for Yield Spread Series.
    """
    def __init__(self, domestic_symbol, foreign_symbol, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.domestic_symbol = domestic_symbol
        self.foreign_symbol = foreign_symbol
        self.domestic_yield_df = FredObject(domestic_symbol, start_date, end_date).to_df()
        self.foreign_yield_df = FredObject(foreign_symbol, start_date, end_date).to_df()
        self.yield_spread_df = self.__get_spread()
    def __repr__(self):
        return f'YieldSpreadObject({self.domestic_symbol}, {self.foreign_symbol}, {self.start_date}, {self.end_date})'
    def __get_title(self, symbol):
        title = FredObject(symbol, self.start_date, self.end_date).series_info['seriess'][0]['title']
        return title
    def __get_spread(self):
        """
        Calculates the yield spread between the domestic and foreign yield DataFrames. 
        """
        spread_df = self.domestic_yield_df[['value']].rename(columns={'value': self.domestic_symbol}).merge(
            self.foreign_yield_df[['value']].rename(columns={'value': self.foreign_symbol}), left_index=True, right_index=True, how='inner'
        )
        spread_df[self.foreign_symbol] = self.foreign_yield_df['value']
        spread_df['spread'] = spread_df[self.domestic_symbol] - spread_df[self.foreign_symbol]
        del spread_df[self.domestic_symbol]
        del spread_df[self.foreign_symbol]
        spread_df = spread_df.rename(columns={'spread': 'value'})
        return spread_df.dropna().ffill()
    def plot_df(self, width=10, height=6):
        """
        Plots the data from the DataFrame.
        """
        self.yield_spread_df['value'].plot(title=f'{self.__get_title(self.domestic_symbol)} - {self.__get_title(self.foreign_symbol)} Spread', figsize=(width, height))
        plt.xlabel('Date')
        plt.ylabel('Value')
        return plt.show()

class CompositeIndexObject:
    """
    Data Object for Composite Index Series.
    """
    def __init__(self, *args):
        self.components = {}
        for arg in args:
            if not isinstance (arg, DataFrame):
                raise TypeError(f'{arg} is not a Pandas DataFrame')
            arg_df = arg.ffill().dropna()
            if "value" not in arg_df.columns:
                raise ValueError(f'{arg} does not have a value column')
            arg_z_scores_df = self.__calculate_z_scores(arg_df)
            self.components[f'{arg}'] = arg_z_scores_df
    def __repr__(self):
        return f"CompositeIndexObject with {len(self.components)} components"
    def __calculate_z_scores(self, df):
        df["value"] = pd.to_numeric(df["value"], errors='coerce')
        df["z-score"] = zscore(df["value"])
        df["z-score"] = pd.Series(df["z-score"].values, index=df.index)
        return df
    def calculate_weighted_output(self, *args):
        """
        Calculate the weighted index output of z-scores based on the provided weights for the 
        dataframe components.
        """
        if len(args) != len(self.components):
            raise ValueError("Number of arguments does not match the number of components")
        weighted_output = pd.Series(0, index=next(iter(self.components.values())).index)
        for weight, (_, df) in zip(args, self.components.items()):
            weighted_output += weight * df["z-score"]
        return weighted_output.to_frame(name='value')
    def plot_weighted_output(self, *args, title, width=10, height=6):
        """
        Plot the weighted index output of z-scores based on the provided weights for the dataframe 
        components.
        """
        weighted_output_df = self.calculate_weighted_output(*args)
        plt.figure(figsize=(width, height))
        weighted_output_df['value'].plot()
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.grid(True)
        return plt.show()
