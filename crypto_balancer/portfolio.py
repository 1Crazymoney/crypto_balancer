class Portfolio():

    def __init__(self, targets, exchange, threshold=1.0, quote_currency="USDT"):
        self.targets = targets
        self.threshold = threshold
        self.exchange = exchange
        self.quote_currency = quote_currency
        self.sync_balances()
        self.sync_rates()

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
        _valuation_quote = self.valuation_quote

        def _calc_pct(cur):
            if _valuation_quote:
                return (_balances_quote[cur] / _valuation_quote) * 100.0
            return 0
        
        return {cur: _calc_pct(cur) for cur in self.currencies}

    @property
    def differences_quote(self):
        # first convert the amounts into their base value
        _total = self.valuation_quote
        _balances_quote = self.balances_quote
        _diff = lambda cur: _total*(self.targets[cur]/100.0) \
                - _balances_quote[cur]
        return {cur: _diff(cur) for cur in self.currencies}

    
