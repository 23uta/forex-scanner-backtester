# forex Scanner & Backtester

An automated algorithmic trading scanner and backtesting engine developed in Python. This tool processes historical financial market data (specifically tailored for Gold XAU/USD 5-minute intervals) to automatically identify critical Supply and Demand zones using Relative Strength Index (RSI) extremes and volume/body price action momentum. 

It executes an automated backtest simulation on the discovered zones, calculates trading statistics, generates an account equity curve, and visualizes the results.

## 🚀 Features

- **Automated Market Scan:** Scans CSV market data for strong institutional momentum candles based on moving averages.
- **Smart Zone Identification:** Detects **Demand Zones** (Oversold RSI + strong bullish engulfing momentum) and **Supply Zones** (Overbought RSI + strong bearish engulfing momentum).
- **Backtesting Engine:** Simulates trade execution when prices mitigate back into identified zones, calculating wins and losses dynamically based on structural highs/lows.
- **Performance Reporting:** Outputs a clear console report with total zones found, total trades executed, and the final Win Rate percentage.
- **Data Visualization:** Generates and saves a high-quality dashboard chart (`trading result.png`) featuring:
  1. An account **Equity Curve** showing balance growth.
  2. A **Win/Loss Distribution** pie chart.
  3. A **Candlestick Chart overlay** visualizing the last 100 market candles with shaded zones (Blue for Demand, Orange for Supply).

## 📊 Technical Architecture & Logic

- **Indicator Engine:** Computes Wilder's RSI alongside a Rolling Window Moving Average for true candlestick body size volatility estimation.
- **Risk Management:** Implements an internal structural Risk-to-Reward ratio system using previous candle extremes for exact Invalidations (Stop Loss) and Target Mitigations (Take Profit).

## 🛠️ Tech Stack & Requirements

The project relies on standard Python libraries specialized in Data Science and Analytics:
- **Pandas** - For efficient file processing, high-speed matrix scanning, and data cleaning.
- **Matplotlib** - For building the analytical charting graphics system.
- **OS Library** - For robust system directory checks.

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git)
   cd YOUR_REPOSITORY_NAME

2.**Install dependencies:**
    
    <<< pip install -r requirements.txt >>>

3.**Prepare Market Data:**
    Place your historical data CSV file named "gold_5m_full_table.csv" in the root directory.

## 📈 Execution
    Run the scanner directly from your terminal:
    
    <<< python main.py >>>
