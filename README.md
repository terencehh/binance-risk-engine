# binance-risk-engine

Rationale

Over 95% of traders lose money. I realized its not due to a lack of strategy that makes traders lose money, its usually the emotional sides of fear & greed which cause people to make stupid decisions like overtrading, oversizing on positions etc, basically lack of risk management. Personally, I have experienced these struggles myself and its very hard to control some of these aspects due to human weakness of fear & greed. This project aims to address the risk side by ensuring a traders account can never blow up with a risk engine script that runs perpetually to ensure account drawdown never exceeds a certain threshold per trade.

Timeline

Phase 1 - Risk Engine Script [COMPLETE]
- Establish binance API connection
- Continuously poll binance futures account balance every second
- If unrealised loss exceeds > 5% of account equity, trigger order API to close all positions
- Configure a cloud service deployment to run the script perpetually + whitelist the IP connection on binance

Phase 2 - Trading Dashboard [TBD]
- PnL Analytics
- TradingView Charts Integration + Binance Order Placement

Setup

Create a Binance Account + setup API key by creating a `.env` file mimicking `env.example`. Run the python script locally or deploy it online via a cloud server. Recommend to run perpetually for maximum effectiveness.