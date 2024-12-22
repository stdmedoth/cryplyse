import pandas as pd
from pytrends.request import TrendReq
import matplotlib.pyplot as plt

# Initialize pytrends
pytrend = TrendReq(hl='pt-BR', tz=240)

# Define keywords
keywords = ["Bitcoin", "BTC",  "Crypto", "Binance", "Ethereum"]
#keywords = ["Bitcoin", "ADA"]
#keywords = ["Bitcoin", "SHIBA", "SHIB", "DOGECOIN", "DOGE"]

# Build payload
#pytrend.build_payload(keywords, timeframe='today 5-y', geo='')
pytrend.build_payload(keywords, timeframe='now 4-H', geo='')

# Fetch interest over time
interest_over_time_df = pytrend.interest_over_time()

# Localize timestamps to UTC and convert to Brasília time
interest_over_time_df.index = interest_over_time_df.index.tz_localize('UTC').tz_convert('America/Sao_Paulo')

print(interest_over_time_df)

# Check if data exists
if not interest_over_time_df.empty:
    # Apply a moving average to smooth the data (window=3)
    smoothed_data = interest_over_time_df[keywords].rolling(window=3, min_periods=1).mean()

    # Compute the derivative (rate of change) for each keyword
    derivatives = smoothed_data.diff().dropna()

    # Define a threshold for sustained increase (based on cumulative growth)
    sustained_increase_threshold = 8  # Total cumulative growth
    sustained_period_threshold = 4     # Minimum number of consecutive periods
    intervals = {}

    for keyword in keywords:
        sustained_intervals = []
        positive_streak = []
        cumulative_growth = 0

        for i, value in enumerate(derivatives[keyword]):
            if value > 0:
                cumulative_growth += value
                positive_streak.append(smoothed_data.index[i])
                if len(positive_streak) >= sustained_period_threshold and cumulative_growth >= sustained_increase_threshold:
                    sustained_intervals.append(positive_streak.copy())
            else:
                cumulative_growth = 0
                positive_streak = []

        # Append the last streak if it qualifies
        if len(positive_streak) >= sustained_period_threshold and cumulative_growth >= sustained_increase_threshold:
            sustained_intervals.append(positive_streak)

        intervals[keyword] = sustained_intervals

    # Plot the trends
    plt.figure(figsize=(12, 6))
    for keyword in keywords:
        plt.plot(interest_over_time_df.index, smoothed_data[keyword], label=f"{keyword} (Smoothed)")

        # Add markers for sustained increase intervals
        for streak in intervals[keyword]:
            plt.scatter(streak, smoothed_data.loc[streak, keyword], s=50)

    plt.title("Google Trends for Bitcoin-related Keywords")
    plt.ylabel("Search Interest")
    plt.xlabel("Date (Brasília Time)")
    plt.legend()
    plt.show()

else:
    print("No data found for the given timeframe.")
