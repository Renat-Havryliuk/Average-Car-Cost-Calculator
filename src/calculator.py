# We calculate the average cost in selected currency
def calculating(price_lists):
    counter = 0
    sum_prices = 0
    for price_list in price_lists:
        if len(price_list) > 0 and price_list[0] != 0:
            for price in price_list:
                sum_prices += price
                counter += 1
    average_price = int(sum_prices / counter)

    return average_price
