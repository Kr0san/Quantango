import numpy as np
import pandas as pd


class Transaction:
    """
    Handles the transaction of an asset, as used in the
    Position class.

    Parameters
    ----------
    asset : `Asset`
        The asset type passed from the asset class.
    quantity : `int`
        Whole number quantity of shares in the transaction
    dt : `pd.to_datetime`
        The date/time of the transaction
    price : `float`
        The transaction price carried out
    order_id : `int`
        The unique order identifier
    commission : `float`, optional
        The trading commission
    """

    def __init__(
        self,
        asset,
        quantity,
        dt,
        price,
        order_id,
        commission=0.0
    ):
        self.asset = asset
        self.quantity = quantity
        self.direction = np.copysign(1, self.quantity)
        if isinstance(dt, str):
            self.dt = pd.to_datetime(dt, dayfirst=True)
        else:
            self.dt = dt
        self.price = price
        self.order_id = order_id
        self.commission = commission

    def __repr__(self):
        """
        Provides a representation of the Transaction
        to allow full recreation of the object.

        Returns
        -------
        `str`
            The string representation of the Transaction.
        """
        return "%s(asset=%s, quantity=%s, dt=%s, " \
            "price=%s, order_id=%s, commission=%s)" % (
                type(self).__name__, self.asset,
                self.quantity, self.dt,
                self.price, self.order_id, self.commission
            )

    @property
    def cost_without_commission(self):
        """
        Calculate the cost of the transaction without including
        any commission costs.

        Returns
        -------
        `float`
            The transaction cost without commission.
        """
        return self.quantity * self.price

    @property
    def cost_with_commission(self):
        """
        Calculate the cost of the transaction including
        any commission costs.

        Returns
        -------
        `float`
            The transaction cost with commission.
        """
        if self.commission == 0.0:
            return self.cost_without_commission
        else:
            return self.cost_without_commission + self.commission
