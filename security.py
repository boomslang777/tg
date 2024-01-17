from datetime import datetime, timedelta
import pandas as pd
from telethon.sync import TelegramClient
from telethon import TelegramClient, events, sync
import time
import re

import telethon
# quantity = 15
import asyncio


def get_exp(contract_name):
    from datetime import datetime, timedelta
    if contract_name == "BANKNIFTY":
        
        current_date = datetime.now()
        day_of_week = current_date.weekday()

        # If it's Tuesday or Wednesday, add 1 or 0 days respectively to get to the next Wednesday
        if day_of_week in [1, 2]:  # 1 corresponds to Tuesday, 2 corresponds to Wednesday
            days_until_nearest_day = (2 - day_of_week + 7) % 7
        else:
            days_until_nearest_day = (2 - day_of_week + 7) % 7  # 2 corresponds to Wednesday

        if (current_date + timedelta(days=days_until_nearest_day)).month != (current_date + timedelta(days=7)).month:
            # Last week of the month, return in the format "YYMON" for Thursday
            return current_date.strftime('%y%b').upper()
        else:
            # Regular case
            nearest_day_date = current_date + timedelta(days=days_until_nearest_day)
            month = nearest_day_date.strftime('%m').lstrip('0')  # Remove leading zero for month
            return nearest_day_date.strftime('%y{0}%d').format(month) + nearest_day_date.strftime('%y%m%d')[6:]

    elif contract_name == "NIFTY":
        current_date = datetime.now()
        day_of_week = current_date.weekday()
        
        # Calculate days until Thursday
        days_until_thursday = (3 - day_of_week + 7) % 7
        nearest_thursday_date = current_date + timedelta(days=days_until_thursday)

        if nearest_thursday_date.month != (nearest_thursday_date + timedelta(days=7)).month:
            # Last week of the month, return in the format "YYMON"
            return nearest_thursday_date.strftime('%y%b')
        else:
            nearest_day_date = current_date + timedelta(days=days_until_nearest_day)
            month = nearest_day_date.strftime('%m').lstrip('0')  # Remove leading zero for month
            return nearest_day_date.strftime('%y{0}%d').format(month) + nearest_day_date.strftime('%y%m%d')[6:]

async def place_order(instrument, qty,kite,bot):
    print(instrument)
    mark = get_ltp(kite,instrument)
    if qty >0 and qty < 900 :
        order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange="NFO",
                        tradingsymbol=instrument,
                        transaction_type="BUY",
                        quantity=qty,
                        order_type="MARKET",
                        product="MIS",
                        validity="DAY",
                        price=0,
                        trigger_price=0)
        print("Position entered successfully")
        message = f"Position entered successfully {instrument} at {mark} Rs. with order id {order_id}"
        entity = await bot.get_entity(1002140069507)  # Replace 'your_channel_username' with your channel's username
        print(entity.id)
        group_id = entity.id

        # Now use the obtained group_id in the send_message call
        await bot.send_message(group_id, message)
    else :
        legs = qty//900
        if qty%900 != 0 :
            legs += 1
        order_id = kite.place_order(variety=kite.VARIETY_ICEBERG,exchange = "NFO"
                         ,tradingsymbol=instrument,transaction_type = 'BUY',quantity=qty,
                         order_type="MARKET",product="MIS",validity="DAY",
                         iceberg_legs = legs,price =0,trigger_price =0,iceberg_quantity=900)
        print("Position entered successfully")
        message = f"Position entered successfully {tradingsymbol} with order id {order_id}"
        entity = await bot.get_entity(1002140069507)  # Replace 'your_channel_username' with your channel's username
        print(entity.id)
        group_id = entity.id

        # Now use the obtained group_id in the send_message call
        await bot.send_message(group_id, message)


async def place_sl_order(instrument, qty,kite,bot):
    print(instrument)
    mark_price = kite.ltp(f"NFO:{instrument}")[f"NFO:{instrument}"]["last_price"]
    print(instrument)
    if qty >0 and qty< 900 :
        order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange="NFO",
                        tradingsymbol=instrument,
                        transaction_type="SELL",
                        quantity=qty,
                        order_type="SL",
                        product="MIS",
                        validity="DAY",
                        price=mark_price -80,
                        trigger_price=mark_price - 75)
        print("SL placed successfully")   
        message = f"SL entered successfully {instrument} at {mark_price-80} with order id {order_id}"
        entity = await bot.get_entity(1002140069507)  # Replace 'your_channel_username' with your channel's username
        print(entity.id)
        group_id = entity.id

        # Now use the obtained group_id in the send_message call
        await bot.send_message(group_id, message)
    else :
        legs = qty//900
        if qty%900 != 0 :
            legs += 1
        iceberg_qty = qty//legs   
        kite.place_order(variety=kite.VARIETY_ICEBERG,exchange = "NFO"
                         ,tradingsymbol=instrument,transaction_type = 'SELL',quantity=qty,
                         order_type="SL",product="MIS",validity="DAY",
                         iceberg_legs = legs,price =mark_price-80,trigger_price =mark_price-75,iceberg_quantity  = iceberg_qty)
        message = f"SL entered successfully {instrument} with order id {order_id}"
        entity = await bot.get_entity(1002140069507)  # Replace 'your_channel_username' with your channel's username
        print(entity.id)
        group_id = entity.id

        # Now use the obtained group_id in the send_message call
        await bot.send_message(group_id, message)
             

def place_iceberg_limit_order(kite, tradingsymbol, quantity, price):
    """
    Place an iceberg order.

    Parameters:
    kite (KiteConnect): The KiteConnect instance.
    tradingsymbol (str): The trading symbol.
    quantity (int): The total quantity.
    order_type (str): The order type ('MARKET' or 'LIMIT').
    price (float, optional): The price for limit orders.
    """
    mark = get_ltp(kite,tradingsymbol)
    # Calculate the number of legs
    if quantity >0 and quantity < 900 :
        kite.place_order(variety=kite.VARIETY_REGULAR, exchange="NFO",
                        tradingsymbol=tradingsymbol,
                        transaction_type="BUY",
                        quantity=quantity,
                        order_type="LMT",
                        product="MIS",
                        validity="DAY",
                        price=mark)
        print("Position entered successfully")
    else : 
        legs = quantity // 900
        if quantity % 900 != 0:
            legs += 1
        iceberg_qty = quantity//legs
        # Place the order
        try:
            order_id = kite.place_order(
                tradingsymbol=tradingsymbol,
                quantity=quantity,
                order_type='LIMIT',
                price=price,
                product=kite.PRODUCT_MIS,
                exchange=kite.EXCHANGE_NSE,
                transaction_type=kite.TRANSACTION_TYPE_BUY,
                validity=kite.VALIDITY_DAY,
                disclosed_quantity=iceberg_qty,
                tag="Iceberg",
                variety=kite.VARIETY_ICEBERG,
                iceberg_legs = legs,iceberg_quantity = iceberg_qty
            )
            print(f"Order placed successfully. Order ID: {order_id}.")
        except Exception as e:
            print(f"An error occurred while placing the order: {e}")


def ctc(kite):
    positions = kite.positions()['net']

# Fetch the orders
    orders = kite.orders()

    # Filter for open orders
    open_orders = [order for order in orders if order['status'] == 'OPEN']

    if not open_orders:
        print("No open orders found.")
    else:
        # Get the latest open order
        latest_order = open_orders[-1]

        # Find the corresponding position
        for position in positions:
            if position['tradingsymbol'] == latest_order['tradingsymbol'] and position['product'] == latest_order['product']:
                average_price = position['average_price']
                break
        else:
            print("No open position found for the latest order.")
            return

        # Modify the order
        try:
            kite.modify_order(
                order_id=latest_order['order_id'],
                parent_order_id=latest_order['parent_order_id'],
                order_type=latest_order['order_type'],
                price=average_price,  # Set the limit price to the average price
                trigger_price=average_price+10,  # Set the trigger price to the average price
                validity=kite.VALIDITY_DAY,
                disclosed_quantity=latest_order['disclosed_quantity']
            )
            print(f"Order {latest_order['order_id']} modified successfully.")
        except Exception as e:
            print(f"An error occurred while modifying order {latest_order['order_id']}: {e}")

def move_sl(kite):
    # Fetch current positions
    positions = kite.positions()

    # Iterate through each position type ('net', 'day')
    for position_type in ['net']:
        # Iterate through positions of the current type
        for position in positions.get(position_type, []):
            # Extract relevant information
            tradingsymbol = position['tradingsymbol']
            quantity = position['quantity']
            average_price = position['average_price']  # Entry price

            if quantity > 0:
                # Place a stop loss order at the entry price
                sl_order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                               exchange=kite.EXCHANGE_NFO,
                                               tradingsymbol=tradingsymbol,
                                               transaction_type=kite.TRANSACTION_TYPE_SELL,
                                               quantity=quantity,
                                               product=kite.PRODUCT_MIS,
                                               order_type=kite.ORDER_TYPE_SL,
                                               trigger_price=average_price+10,
                                               price = average_price,
                                               tag="StopLoss")

                # Print information about the stop loss order
                print(f"Stop loss order placed at entry price for {tradingsymbol} with order id {sl_order_id}")
            else:
                print("No position to place stop loss")
    
    
def get_stk(condition,kite):
    print(condition)
    banknifty_ltp = kite.ltp("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
    print(banknifty_ltp)
    strike_price = round(banknifty_ltp / 100) * 100
    print(f"{strike_price} is strike price")

    if condition == "BUY":
        return strike_price + 100
    elif condition == "SELL":
        return strike_price - 100
    else:
        return strike_price

def cancel_orders(kite):
    orders = kite.orders()
    print(orders)
    for order in orders:
        if order["status"] == "OPEN" and order["pending_quantity"] > 0:
            order_id = order["order_id"]
            print(order_id)
            kite.cancel_order(kite.VARIETY_REGULAR, order_id)
            print(f"Order {order_id} cancelled")


async def square_off_all_positions(kite,bot):
    # Fetch current positions
    positions =  kite.positions()
    # Iterate through each position type ('net', 'day')
    for position_type in ['net']:
        # Iterate through positions of the current type
        for position in positions.get(position_type, []):
            # Extract relevant information
            tradingsymbol = position['tradingsymbol']
            quantity = position['quantity']
            if quantity > 0 and quantity < 900:
                # Place a market sell order to square off the position
                order_id = await kite.place_order(variety=kite.VARIETY_REGULAR,
                                            exchange=kite.EXCHANGE_NFO,
                                            tradingsymbol=tradingsymbol,
                                            transaction_type=kite.TRANSACTION_TYPE_SELL,
                                            quantity=quantity,
                                            product=kite.PRODUCT_MIS,
                                            order_type=kite.ORDER_TYPE_MARKET,
                                            tag="SquareOff")

                # Print information about the square off order
                message = f"Square off order placed for {tradingsymbol} with order id {order_id}"
                entity = await bot.get_entity(1002140069507)  # Replace 'your_channel_username' with your channel's username
                print(entity.id)
                group_id = entity.id

                # Now use the obtained group_id in the send_message call
                await bot.send_message(group_id, message)
            else :
                legs = quantity//900
                # remaining_qty = quantity % 900
                order_id = await kite.place_order(variety=kite.VARIETY_ICEBERG,exchange=kite.EXCHANGE_NFO,tradingsymbol=tradingsymbol,transaction_type=kite.TRANSACTION_TYPE_SELL,quantity=quantity,product=kite.MIS,iceberg_legs=legs+1,order_type=kite.ORDER_TYPE_MARKET)
                print("All orders squared off")
                message = "All positions squared off"
                entity = await bot.get_entity(1002140069507)  # Replace 'your_channel_username' with your channel's username
                print(entity.id)
                group_id = entity.id

                # Now use the obtained group_id in the send_message call
                await bot.send_message(group_id, message)
    
# def fire(condition,kite,bot):
#     if condition == 1:
#         direction = "BUY"
#         option_type = "CE"
#     elif condition == -1:
#         direction = "SELL"
#         option_type = "PE"
#     exp = get_exp("BANKNIFTY").upper()
#     stk = get_stk(direction,kite)
#     contract_name = "BANKNIFTY"
#     order_info = f"{contract_name}{exp}{stk}{option_type}"
#     ltp = get_ltp(kite,order_info)
#     place_order(order_info, quantity,kite)
#     place_sl_order(order_info,quantity,kite)
    

    
    
# async def fire(condition, kite, bot):
#     try:
#         if condition == 1 or condition == -1:
#             direction = "BUY" if condition == 1 else "SELL"
#             option_type = "CE" if condition == 1 else "PE"
#             exp = get_exp("BANKNIFTY").upper()
#             stk = get_stk(direction, kite)
#             contract_name = "BANKNIFTY"
#             order_info = f"{contract_name}{exp}{stk}{option_type}"
#             ltp = get_ltp(kite,order_info)  # Set the desired quantity
#             message = f"Direction: {direction}\nOrder Info: {order_info}\nQuantity: {quantity}\nLTP : {ltp}\nDo you want to proceed? (Type /yes to confirm)"
#             entity = await bot.get_entity(1002140069507)  # Replace 'my channel numeric id' with your channel's numeric id
#             # entity = await bot.get_entity()
#             print(entity.id)
#             group_id = entity.id

#             # Now use the obtained group_id in the send_message call
#             await bot.send_message(group_id, message)
#             @bot.on(events.NewMessage(chats=group_id))
#             async def handle_new_message(event):
#                 sender = await event.get_sender()
#                 print(f'Username: {sender.username}, Message: {event.message.text}')
#             # Wait for user input
#             #response = await TelegramClient.get_messages(1002140069507, limit=1)
#             # response = await bot.get_messages(1002140069507, limit=1)
#             # #response = await bot.get_messages(1002140069507, limit=1)
#             # print(response)
#             # if response and len(response) > 0 and (await response[0]).text == '/yes':
#             # #if response and (await response[0]).text == '/yes':
#             #     await place_order(order_info, quantity, kite)
#             #     await place_sl_order(order_info, quantity, kite)
#             # else:
#             #     print("User did not confirm. Skipping order placement.")
#     except telethon.errors.rpcerrorlist.PeerIdInvalidError as e:
#         print(f"An error occurred: {str(e)}. Check the group_id and bot permissions.")



async def calculate_and_send_pnl(kite, group_id, bot):
    while True:
        try:
            positions = kite.positions()['net']
            orders = kite.orders()

            for position in positions:
                trading_symbol = position['tradingsymbol']
                quantity = position['quantity']

                # Check if there is an open position
                has_open_position = quantity != 0

                # Check if the SL order is hit
                

                if has_open_position :
                    pnl = position['pnl']
                    print(f"PnL for {trading_symbol}: ", pnl)
                    await bot.send_message(group_id, f"PnL for {trading_symbol}: {pnl}")
                else:
                    print("No open positions")
                    break

            await asyncio.sleep(60)  # Adjust the sleep duration as needed

        except Exception as e:
            print(f"An error occurred while calculating P&L: {e}")
            # Add appropriate error handling logic here

async def fire(condition, kite, bot):
    try:
        if condition == 1 or condition == -1:
            direction = "BUY" if condition == 1 else "SELL"
            option_type = "CE" if condition == 1 else "PE"
            exp = get_exp("BANKNIFTY").upper()
            stk = get_stk(direction, kite)
            contract_name = "BANKNIFTY"
            order_info = f"{contract_name}{exp}{stk}{option_type}"
            ltp = get_ltp(kite, order_info)
            quantity = 15  # Set the desired quantity (you need to define the quantity here)
            margin = quantity * ltp
            message = f"Direction: {direction}\nOrder Info: {order_info}\nQuantity: {quantity}\nLTP : {ltp}\nDo you want to proceed? (Type /yes to confirm),\n{margin} is margin"
            entity = await bot.get_entity(1002140069507)  # Replace 'your_channel_username' with your channel's username
            print(entity.id)
            group_id = entity.id
            print(f"{order_info} is order info")
            
            # Now use the obtained group_id in the send_message call
            await bot.send_message(group_id, message)

            @bot.on(events.NewMessage(chats=group_id))
            async def handle_new_message(event, order_info=order_info, quantity=quantity):
                sender = await event.get_sender()
                print(f'Username: {sender.username}, Message: {event.message.text}')

                market_order_regex = re.compile(r'/MKT/(\d+)/([+-]?\d+)')
                limit_order_regex = re.compile(r'/LMT/([+-]?\d+(\.\d+)?)/(\d+)/([+-]?\d+)')

                match_market_order = market_order_regex.match(event.message.text)
                match_limit_order = limit_order_regex.match(event.message.text)

                if match_market_order:
                    quantity = int(match_market_order.group(1))
                    strike = int(match_market_order.group(2))
                    banknifty_ltp = kite.ltp("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
                    stkm = int(round(banknifty_ltp + strike, -2))
                    order_info = f"{contract_name}{exp}{stkm}{option_type}"
                    print(f"Market Order - Quantity: {quantity}, Strike: {stkm}")
                    print("Placing trades")
                    await place_order(order_info, quantity, kite,bot)
                    print("Order placed")
                    await place_sl_order(order_info, quantity, kite)
                    print("SL placed")

                    # Integrate P&L streaming
                    await calculate_and_send_pnl(kite, group_id, bot)

                elif match_limit_order:
                    price = float(match_limit_order.group(1))
                    quantity = int(match_limit_order.group(3))
                    strike = int(match_limit_order.group(4))
                    banknifty_ltp = kite.ltp("NSE:NIFTY BANK")["NSE:NIFTY BANK"]["last_price"]
                    stkl = int(round(banknifty_ltp + strike, -2))
                    order_info = f"{contract_name}{exp}{stkl}{option_type}"
                    print(f"Limit Order - Price: {price}, Quantity: {quantity}, Strike: {strike}")
                    order_id = await place_iceberg_limit_order(kite, order_info, quantity, price)
                    order = kite.order_history(order_id)
                    status = order['status']
                    print("Order Status: ", status)
                    while True:
                        orders = kite.orders()
                        open_orders = [order for order in orders if order['status'] == 'OPEN']
                        if not open_orders:
                            print("No open orders found.")
                            print("Placing SL")
                            place_sl_order(order_info, quantity, kite)
                            break
                        else:
                            # Get the latest open order
                            latest_order = open_orders[-1]
                            time.sleep(1)
                            continue
                            # Add your logic for limit order here

                elif event.message.text == '/yes':
                    print("Placing trades")
                    await place_order(order_info, quantity, kite,bot)
                    print("Order placed")
                    await place_sl_order(order_info, quantity, kite,bot)
                    print("SL placed")

                    # Integrate P&L streaming
                    await calculate_and_send_pnl(kite, group_id, bot)

            await bot.run_until_disconnected()

    except Exception as e:
        print(f"An error occurred: {e}")


# print(get_exp("BANKNIFTY"))
def get_ltp(kite,instrument):
    ltp = kite.ltp(f"NFO:{instrument}")[f"NFO:{instrument}"]["last_price"]
    return ltp
