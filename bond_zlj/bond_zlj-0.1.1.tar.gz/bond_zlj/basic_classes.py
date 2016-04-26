from functions import pricing

class Bond:
    par_value = 100
    coupon_rate = 0.05
    maturity = 5
    price = 100
    ytm = 0.05
    interval = 1

    def __init__(self, par_value=100, coupon_rate=0.05, maturity=5, price=100, ytm=0.05, interval=1):
        self.par_value = par_value
        self.coupon_rate = coupon_rate
        self.maturity = maturity
        self.price = price
        self.ytm = ytm
        self.interval = interval

    def calc_price(self):
        self.price = pricing(self.par_value, self.coupon_rate, self.maturity, self.ytm, self.interval)
        return self.price

    def calc_ytm(self):
        grid = [0.0001 * x for x in range(1, 2000)]
        price_grid = [pricing(self.par_value, self.coupon_rate, self.maturity, x, self.interval) for x in grid]
        index, price = reduce(lambda x, y: x if abs(x[1] - self.price) < abs(y[1] - self.price) else y, enumerate(price_grid))
        self.ytm = grid[index] / self.interval
        return self.ytm
