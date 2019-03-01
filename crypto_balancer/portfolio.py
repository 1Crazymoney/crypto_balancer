import math

class Portfolio():

    @classmethod
    def make_portfolio(cls, targets, exchange,
                       threshold=1.0, quote_currency="USDT"):
        p = cls(targets, exchange, threshold, quote_currency)
        p.sync_balances()
        p.sync_rates()
        return p

    def __init__(self, targets, exchange, threshold=1.0,
                 quote_currency="USDT"):
        self.targets = targets
        self.threshold = threshold
        self.exchange = exchange
        self.quote_currency = quote_currency
        self.balances = {}
        self.rates = {}

    def copy(self):
        p = Portfolio(self.targets,
                      self.exchange,
                      self.threshold,
                      self.quote_currency)
        p.balances = self.balances.copy()
        p.rates = self.rates.copy()
        return p

    def sync_balances(self):
        self.balances = self.exchange.balances.copy()

    def sync_rates(self):
        self.rates = self.exchange.rates.copy()

    @property
    def currencies(self):
        return self.targets.keys()

    @property
    def balances_quote(self):
        _balances_quote = {}
        for cur, amount in self.balances.items():
            if cur == self.quote_currency:
                _balances_quote[cur] = amount
            else:
                pair = "{}/{}".format(cur, self.quote_currency)
                if pair not in self.rates:
                    raise ValueError("Invalid pair: {}".format(pair))
                _balances_quote[cur] = amount * self.rates[pair]

        return _balances_quote

    @property
    def valuation_quote(self):
        return sum(self.balances_quote.values())

    @property
    def needs_balancing(self):
        _current_percentages = self.balances_pct
        for cur in self.currencies:
            if abs(self.targets[cur] - _current_percentages[cur]) \
               > self.threshold:
                return True
        return False

    @property
    def balances_pct(self):
        # first convert the amounts into their base value
        _balances_quote = self.balances_quote
        _total = self.valuation_quote

        if not _total:
            return {cur: 0 for cur in self.currencies}

        return {cur: (_balances_quote[cur] / _total) * 100.0
                for cur in self.currencies}

    @property
    def balance_rmse(self):
        _total = self.valuation_quote
        _balances_quote = self.balances_quote

        if not _total:
            return 0

        def calc_diff(cur):
            return _total*(self.targets[cur]/100.0) \
                - _balances_quote[cur]

        pcts = [(calc_diff(cur) / _total) * 100.0
                for cur in self.currencies]
        dev = math.sqrt(sum([x**2 for x in pcts]) / len(pcts))
        return dev

    @property
    def differences_quote(self):
        # first convert the amounts into their base value
        _balances_quote = self.balances_quote
        _total = self.valuation_quote

        def calc_diff(cur):
            return _total*(self.targets[cur]/100.0) \
                - _balances_quote[cur]

        return {cur: calc_diff(cur) for cur in self.currencies}