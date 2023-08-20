import numpy as np
import quantstats as qs


def omega(returns, rf=0.0, required_return=0.0, periods=252):
    """
    Determines the Omega ratio of a strategy.
    See https://en.wikipedia.org/wiki/Omega_ratio for more details.
    """
    if len(returns) < 2:
        return np.nan

    if required_return <= -1:
        return np.nan

    returns = qs.utils._prepare_returns(returns, rf, periods)

    if periods == 1:
        return_threshold = required_return
    else:
        return_threshold = (1 + required_return) ** (1.0 / periods) - 1

    returns_less_thresh = returns - return_threshold
    numer = returns_less_thresh[returns_less_thresh > 0.0].sum()
    denom = -1.0 * returns_less_thresh[returns_less_thresh < 0.0].sum()

    if denom > 0.0:
        return numer / denom

    return np.nan
