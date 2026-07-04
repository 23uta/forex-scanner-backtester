import pandas as pd
import os
import matplotlib.pyplot as plt

# You can change these settings for different scan
SETTINGS = {
    "file_path": "gold_5m_full_table.csv",
    "rsi_period": 14,
    "rsi_oversold": 35,
    "rsi_overbought": 70,
    "body_multiplier": 1.5,
    "avg_window": 20,
    "initial_balance": 1000  # Added for plotting equity
}

class GoldScanner:
    def __init__(self, config):
        self.config = config
        self.df = None
        self.equity_curve = [config["initial_balance"]] # Track balance
        self.results = {
            "demands": [],
            "supplies": [],
            "stats": {
                "buy_win": 0, "buy_fail": 0,
                "sell_win": 0, "sell_fail": 0
            }
        }

    def load_data(self):
        # checking and loading the data file
        if not os.path.exists(self.config["file_path"]):
            raise FileNotFoundError(f"Error: {self.config['file_path']} not found!")
        
        self.df = pd.read_csv(self.config["file_path"])
        # cleaning the file from empty cells ( if exist)
        self.df.dropna(inplace=True)
        return self.df

    def apply_indicators(self):
        # calculating RSI , body avg
        df = self.df
        # calculating RSI using wilders method
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))
        avg_gain = gain.ewm(alpha=1/self.config["rsi_period"], adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.config["rsi_period"], adjust=False).mean()
        
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # calculating candles body avg
        df['Body'] = abs(df['Close'] - df['Open'])
        df['Avg_Body'] = df['Body'].rolling(window=self.config["avg_window"]).mean()
        self.df = df

    def scan(self):
        # scanners engine
        df = self.df
        for i in range(self.config["avg_window"], len(df)):
            curr = df.iloc[i]
            prev = df.iloc[i-1]
            
            # 1.detecting zones
            is_strong = curr['Body'] > (curr['Avg_Body'] * self.config["body_multiplier"])
            
            # demand zone (Buy)
            if is_strong and curr['Close'] > curr['Open'] and curr['RSI'] <= self.config["rsi_oversold"]:
                self.results["demands"].append({
                    "discovery_idx": i,
                    "high": prev['High'], "low": prev['Low'],
                    "status": "Fresh"
                })
            
            # supply zone (Sell)
            elif is_strong and curr['Close'] < curr['Open'] and curr['RSI'] >= self.config["rsi_overbought"]:
                self.results["supplies"].append({
                    "discovery_idx": i,
                    "high": prev['High'], "low": prev['Low'],
                    "status": "Fresh"
                })

            # 2.Backtesting logic
            self._update_trades(curr, i)

    def _update_trades(self, curr, i):
        # buy (bull) trades check
        for zone in self.results["demands"]:
            if zone["status"] == "Fresh" and i > zone["discovery_idx"]:
                if curr['Low'] <= zone['high']:
                    zone["status"] = "Touched"
                    zone["t_idx"] = i
            elif zone["status"] == "Touched" and i > zone["t_idx"]:
                t_high = self.df.iloc[zone["t_idx"]]['High']
                if curr['High'] >= t_high:
                    self.results["stats"]["buy_win"] += 1
                    zone["status"] = "Success"
                    self.equity_curve.append(self.equity_curve[-1] + 20) # Simulate profit
                elif curr['Low'] <= zone['low']:
                    self.results["stats"]["buy_fail"] += 1
                    zone["status"] = "Failed"
                    self.equity_curve.append(self.equity_curve[-1] - 10) # Simulate loss

        # sell (bear) trades check
        for zone in self.results["supplies"]:
            if zone["status"] == "Fresh" and i > zone["discovery_idx"]:
                if curr['High'] >= zone['low']:
                    zone["status"] = "Touched"
                    zone["t_idx"] = i
            elif zone["status"] == "Touched" and i > zone["t_idx"]:
                t_low = self.df.iloc[zone["t_idx"]]['Low']
                if curr['Low'] <= t_low:
                    self.results["stats"]["sell_win"] += 1
                    zone["status"] = "Success"
                    self.equity_curve.append(self.equity_curve[-1] + 20)
                elif curr['High'] >= zone['high']:
                    self.results["stats"]["sell_fail"] += 1
                    zone["status"] = "Failed"
                    self.equity_curve.append(self.equity_curve[-1] - 10)

    def plot_results(self):

        #Plots Equity Curve, Win/Loss Distribution, and Sample Zones
        
        fig = plt.figure(figsize=(15, 10))
        plt.subplots_adjust(hspace=0.4)

        # 1. Equity Curve
        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(self.equity_curve, color='green', linewidth=2)
        ax1.set_title("Equity Curve (Account Growth)")
        ax1.set_ylabel("Balance ($)")

        # 2. Win/Loss Distribution Pie Chart
        ax2 = plt.subplot(2, 2, 2)
        s = self.results["stats"]
        wins = s["buy_win"] + s["sell_win"]
        fails = s["buy_fail"] + s["sell_fail"]
        if (wins + fails) > 0:
            ax2.pie([wins, fails], labels=['Wins', 'Losses'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=90)
            ax2.set_title("Overall Win/Loss Distribution")

        # 3. Candlestick Chart with Zones (Sample of last 100 candles)
        ax3 = plt.subplot(2, 1, 2)
        sample_df = self.df.tail(100).copy()
        sample_df = sample_df.reset_index()
        
        # Plotting basic candles
        for idx, row in sample_df.iterrows():
            color = 'green' if row['Close'] > row['Open'] else 'red'
            ax3.vlines(idx, row['Low'], row['High'], color=color, linewidth=1)
            ax3.vlines(idx, row['Open'], row['Close'], color=color, linewidth=4)

        # Overlay detected zones that appear in the tail
        last_idx = self.df.index[-1]
        for zone in self.results["demands"] + self.results["supplies"]:
            if zone["discovery_idx"] > (last_idx - 100):
                rel_idx = zone["discovery_idx"] - (last_idx - 100)
                color = 'blue' if zone in self.results["demands"] else 'orange'
                ax3.axhspan(zone['low'], zone['high'], xmin=rel_idx/100, alpha=0.3, color=color)

        ax3.set_title("Last 100 Candles with Detected Zones (Blue: Demand, Orange: Supply)")
        plt.savefig("trading result.png")

    def report(self):
        # results report
        s = self.results["stats"]
        total_win = s["buy_win"] + s["sell_win"]
        total_fail = s["buy_fail"] + s["sell_fail"]
        total = total_win + total_fail
        
        print("\n" + "="*41)
        print("    --- GOLD SCANNER FINAL REPORT ---")
        print("="*41)
        print(f"Total Demand Zones: {len(self.results['demands'])}")
        print(f"Total Supply Zones: {len(self.results['supplies'])}")
        print("-" * 20)
        print(f"Successful Trades: {total_win}")
        print(f"Failed Trades:     {total_fail}")
        
        if total > 0:
            win_rate = (total_win / total) * 100
            print(f"WIN RATE: {win_rate:.2f}%")
        print("="*40 + "\n")

# ===========================================
#                  EXECUTION
# ===========================================
if __name__ == "__main__":
    scanner = GoldScanner(SETTINGS)
    try:
        scanner.load_data()
        scanner.apply_indicators()
        print(" Starting Scan...")
        scanner.scan()
        scanner.report()
        scanner.plot_results() # Added function call
    except Exception as e:
        print(f"An error occurred: {e}")