import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime
import time

def fetch_and_analyze_trends(keywords, timeframe='now 4-H', geo='', 
                             sustained_increase_threshold=8, sustained_period_threshold=7):
    # Initialize pytrends
    pytrend = TrendReq(hl='pt-BR', tz=240)
    pytrend.build_payload(keywords, timeframe=timeframe, geo=geo)

    # Fetch interest over time
    interest_over_time_df = pytrend.interest_over_time()

    # Check if data exists
    if interest_over_time_df.empty:
        print(f"[{datetime.now()}] No data found for the given timeframe.")
        return None

    # Localize timestamps to UTC and convert to Brasília time
    interest_over_time_df.index = interest_over_time_df.index.tz_localize('UTC').tz_convert('America/Sao_Paulo')

    # Apply a moving average to smooth the data (window=3)
    smoothed_data = interest_over_time_df[keywords].rolling(window=3, min_periods=1).mean()

    # Compute the derivative (rate of change) for each keyword
    derivatives = smoothed_data.diff().dropna()

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

    # Alert if any sustained interval is found
    for keyword, streaks in intervals.items():
        if streaks:
            print(f"[{datetime.now()}] Alert: Sustained interval found for keyword '{keyword}'!")
            for streak in streaks:
                print(f"  - Streak: {streak}")

    return intervals

def main():
    keywords = ["Bitcoin", "BTC", "Crypto", "Binance", "Ethereum"]
    alert_interval = 10  # Check every 1 hour (in seconds)

    while True:
        print(f"[{datetime.now()}] Running trend analysis...")
        try:
            intervals = fetch_and_analyze_trends(keywords)
            if intervals:
                print(f"[{datetime.now()}] Finished trend analysis.")
        except Exception as e:
            print(f"[{datetime.now()}] Error occurred: {e}")

        # Wait for the next check
        time.sleep(alert_interval)

if __name__ == "__main__":
    main()
