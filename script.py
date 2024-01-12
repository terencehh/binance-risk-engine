import os
import time
from dotenv import load_dotenv
from binance import Client
from datetime import datetime, timedelta
import pytz


def main():
    api_key = os.environ.get('BINANCE_API')
    api_secret = os.environ.get('BINANCE_SECRET')
    client = Client(api_key, api_secret)
    risk_limit = 0.05  # 5% drawdown limit
    drawdown_breached = False
    time_of_breach = None
    # Poll every second
    start_time = time.monotonic()
    while True:
        current_tick = datetime.now(pytz.timezone('Asia/Singapore'))
        account_info = list(filter(lambda x: x['asset'] == 'USDT', client.futures_account_balance()))[0]  # usdt balance
        account_balance = float(account_info['balance'])
        unrealized_pnl = float(account_info['crossUnPnl'])
        print('Time: {} - Equity: {} - Unrealized Equity: {} - Drawdown Threshold: {}'.format(
            current_tick.strftime('%Y-%m-%d %H:%M:%S'),
            account_balance,
            account_balance + unrealized_pnl,
            account_balance * (1 - risk_limit)))

        # if drawdown has already been breached and current time is not 24 hours past breached time
        if drawdown_breached:
            print('Drawdown breached previously at {}, cooling off in effect until: {}'.format(
                time_of_breach.strftime('%Y-%m-%d %H:%M:%S'),
                (time_of_breach + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
            ))
            if (current_tick - timedelta(hours=24)) > time_of_breach:
                print('24 Hours past previous breach, resetting flags now')
                drawdown_breached = False
                time_of_breach = None
            else:
                # force close any new positions to simulate cooling-off period for one day
                close_all_positions(client)
        else:
            if (account_balance + unrealized_pnl) < (account_balance * (1 - risk_limit)):
                print('Drawdown limit breached')
                close_all_positions(client)
                drawdown_breached = True
                time_of_breach = current_tick

        # sleep until next second
        time.sleep(1.0 - ((time.monotonic() - start_time) % 1.0))


def close_all_positions(client: Client) -> None:
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


if __name__ == "__main__":
    load_dotenv()
    main()
