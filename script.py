import os
import time
from dotenv import load_dotenv
from binance import Client
from datetime import datetime
import pytz


def main():
    api_key = os.environ.get('BINANCE_API')
    api_secret = os.environ.get('BINANCE_SECRET')
    client = Client(api_key, api_secret)
    risk_limit = 0.05  # 5% drawdown limit

    # Poll every second
    start_time = time.monotonic()
    while True:
        # fetch account balance in usdt
        account_info = list(filter(lambda x: x['asset'] == 'USDT', client.futures_account_balance()))[0]
        account_balance = float(account_info['balance'])
        unrealized_pnl = float(account_info['crossUnPnl'])

        print('Time: {} - Equity: {} - Unrealized Equity: {} - Drawdown Threshold: {}'.format(
            datetime.now(pytz.timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S'),
            account_balance,
            account_balance + unrealized_pnl,
            account_balance * (1 - risk_limit)))

        # drawdown breached, close all positions
        if (account_balance + unrealized_pnl) < (account_balance * (1 - risk_limit)):
            print('drawdown limit breached, closing all positions immediately')

            # Fetch positions
            position_info = list(filter(lambda x: float(x['positionAmt']) != 0, client.futures_position_information()))

            # Iterate through positions and close them by placing opposite orders in the same amount
            for position in position_info:
                client.futures_create_order(
                    symbol=position['symbol'],
                    side='SELL' if float(position['positionAmt']) > 0 else 'BUY',
                    type='MARKET',
                    quantity=abs(float(position['positionAmt'])),
                    reduceOnly="true",
                )
                print('Market Closed {} {} position'.format(position['symbol'],
                                                            'Long' if float(position['positionAmt']) > 0 else 'Short'))

        # sleep until next second
        time.sleep(1.0 - ((time.monotonic() - start_time) % 1.0))


if __name__ == "__main__":
    load_dotenv()
    main()
