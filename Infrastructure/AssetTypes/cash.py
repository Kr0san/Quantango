from Infrastructure.AssetTypes.asset import Asset


class Cash(Asset):
    """
    Stores metadata about a cash asset.

    :param currency:    The currency of the Cash Asset. Defaults to USD.
    :type  currency:    str, optional
    """

    def __init__(self, currency='USD'):
        self.cash_like = True
        self.currency = currency
