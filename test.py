from ib_insync import IB, MarketOrder, OrderCondition, Order, Option

def place_orders(form_data, ib):
    instrument = form_data['instrument']
    strike = form_data['strike']
    expiry = form_data['expiry']
    lots = form_data['lots']
    incremental_lots = form_data['incremental_lots']
    SL = form_data['SL']
    TP = form_data['TP']

    # Create the option contract
    option = Option('BANKNIFTY', expiry, strike, 'C', 'NSE')

    # Qualify the contract
    ib.qualifyContracts(option)

    # Request market data
    market_data = ib.reqMktData(option)

    # Assuming you have a function to get the freeze quantity
    freeze_quantity = get_freeze_quantity(instrument)

    # Order slicing based on freeze quantity
    while lots > 0:
        if lots > freeze_quantity:
            # Place order for freeze quantity
            order = MarketOrder('BUY', freeze_quantity)
            ib.placeOrder(option, order)
            lots -= freeze_quantity
        else:
            # Place order for remaining lots
            order = MarketOrder('BUY', lots)
            ib.placeOrder(option, order)
            lots = 0

    # If SL and TP are given, place bracket orders
    if SL and TP:
        # Create the parent bracket order
        parent = LimitOrder('BUY', lots, price)
        parent.transmit = False

        # Create the take profit order
        takeProfit = LimitOrder('SELL', lots, TP)
        takeProfit.parentId = parent.orderId
        takeProfit.transmit = False

        # Create the stop loss order
        stopLoss = StopOrder('SELL', lots, SL)
        stopLoss.parentId = parent.orderId
        stopLoss.transmit = True

        # Place the bracket order
        for o in [parent, takeProfit, stopLoss]:
            ib.placeOrder(option, o)
    else:
        # Else, hit market order
        order = MarketOrder('BUY', lots)
        ib.placeOrder(option, order)

    # Incremental lot size functionality
    while incremental_lots > 0:
        # Place order for incremental lot size
        order = MarketOrder('BUY', incremental_lots)
        ib.placeOrder(option, order)
        incremental_lots -= 1
