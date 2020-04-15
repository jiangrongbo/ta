"""
.. module:: volume
   :synopsis: Volume Indicators.

.. moduleauthor:: Dario Lopez Padial (Bukosabino)

"""

import numpy as np
import pandas as pd

from ta.utils import IndicatorMixin, ema


class AccDistIndexIndicator(IndicatorMixin):
    """Accumulation/Distribution Index (ADI)

    Acting as leading indicator of price movements.

    https://school.stockcharts.com/doku.php?id=technical_indicators:accumulation_distribution_line

    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        fillna(bool): if True, fill nan values.
    """

    def __init__(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, fillna: bool = False):
        self._high = high
        self._low = low
        self._close = close
        self._volume = volume
        self._fillna = fillna
        self._run()

    def _run(self):
        clv = ((self._close - self._low) - (self._high - self._close)) / (self._high - self._low)
        clv = clv.fillna(0.0)  # float division by zero
        ad = clv * self._volume
        self._ad = ad.cumsum()

    def acc_dist_index(self) -> pd.Series:
        """Accumulation/Distribution Index (ADI)

        Returns:
            pandas.Series: New feature generated.
        """
        ad = self._check_fillna(self._ad, value=0)
        return pd.Series(ad, name='adi')


class OnBalanceVolumeIndicator(IndicatorMixin):
    """On-balance volume (OBV)

    It relates price and volume in the stock market. OBV is based on a
    cumulative total volume.

    https://en.wikipedia.org/wiki/On-balance_volume

    Args:
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        fillna(bool): if True, fill nan values.
    """

    def __init__(self, close: pd.Series, volume: pd.Series, fillna: bool = False):
        self._close = close
        self._volume = volume
        self._fillna = fillna
        self._run()

    def _run(self):
        obv = np.where(self._close < self._close.shift(1), -self._volume, self._volume)
        self._obv = pd.Series(obv, index=self._close.index).cumsum()

    def on_balance_volume(self) -> pd.Series:
        """On-balance volume (OBV)

        Returns:
            pandas.Series: New feature generated.
        """
        obv = self._check_fillna(self._obv, value=0)
        return pd.Series(obv, name='obv')


class ChaikinMoneyFlowIndicator(IndicatorMixin):
    """Chaikin Money Flow (CMF)

    It measures the amount of Money Flow Volume over a specific period.

    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:chaikin_money_flow_cmf

    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        n(int): n period.
        fillna(bool): if True, fill nan values.
    """

    def __init__(self, high: pd.Series, low: pd.Series, close: pd.Series,
                 volume: pd.Series, n: int = 20, fillna: bool = False):
        self._high = high
        self._low = low
        self._close = close
        self._volume = volume
        self._n = n
        self._fillna = fillna
        self._run()

    def _run(self):
        mfv = ((self._close - self._low) - (self._high - self._close)) / (self._high - self._low)
        mfv = mfv.fillna(0.0)  # float division by zero
        mfv *= self._volume
        self._cmf = mfv.rolling(self._n, min_periods=0).sum() / self._volume.rolling(self._n, min_periods=0).sum()

    def chaikin_money_flow(self) -> pd.Series:
        """Chaikin Money Flow (CMF)

        Returns:
            pandas.Series: New feature generated.
        """
        cmf = self._check_fillna(self._cmf, value=0)
        return pd.Series(cmf, name='cmf')


class ForceIndexIndicator(IndicatorMixin):
    """Force Index (FI)

    It illustrates how strong the actual buying or selling pressure is. High
    positive values mean there is a strong rising trend, and low values signify
    a strong downward trend.

    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:force_index

    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        n(int): n period.
        fillna(bool): if True, fill nan values.
    """

    def __init__(self, close: pd.Series, volume: pd.Series, n: int = 13, fillna: bool = False):
        self._close = close
        self._volume = volume
        self._n = n
        self._fillna = fillna
        self._run()

    def _run(self):
        fi = (self._close - self._close.shift(1)) * self._volume
        self._fi = ema(fi, self._n, fillna=self._fillna)

    def force_index(self) -> pd.Series:
        """Force Index (FI)

        Returns:
            pandas.Series: New feature generated.
        """
        fi = self._check_fillna(self._fi, value=0)
        return pd.Series(fi, name=f'fi_{self._n}')


class EaseOfMovementIndicator(IndicatorMixin):
    """Ease of movement (EoM, EMV)

    It relate an asset's price change to its volume and is particularly useful
    for assessing the strength of a trend.

    https://en.wikipedia.org/wiki/Ease_of_movement

    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        volume(pandas.Series): dataset 'Volume' column.
        n(int): n period.
        fillna(bool): if True, fill nan values.
    """

    def __init__(self, high: pd.Series, low: pd.Series, volume: pd.Series, n: int = 14, fillna: bool = False):
        self._high = high
        self._low = low
        self._volume = volume
        self._n = n
        self._fillna = fillna
        self._run()

    def _run(self):
        self._emv = (self._high.diff(1) + self._low.diff(1)) * (self._high - self._low) / (2 * self._volume)
        self._emv *= 100000000

    def ease_of_movement(self) -> pd.Series:
        """Ease of movement (EoM, EMV)

        Returns:
            pandas.Series: New feature generated.
        """
        emv = self._check_fillna(self._emv, value=0)
        return pd.Series(emv, name=f'eom_{self._n}')

    def sma_ease_of_movement(self) -> pd.Series:
        """Signal Ease of movement (EoM, EMV)

        Returns:
            pandas.Series: New feature generated.
        """
        emv = self._emv.rolling(self._n, min_periods=0).mean()
        emv = self._check_fillna(emv, value=0)
        return pd.Series(emv, name=f'sma_eom_{self._n}')


class VolumePriceTrendIndicator(IndicatorMixin):
    """Volume-price trend (VPT)

    Is based on a running cumulative volume that adds or substracts a multiple
    of the percentage change in share price trend and current volume, depending
    upon the investment's upward or downward movements.

    https://en.wikipedia.org/wiki/Volume%E2%80%93price_trend

    Args:
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        fillna(bool): if True, fill nan values.
    """

    def __init__(self, close: pd.Series, volume: pd.Series, fillna: bool = False):
        self._close = close
        self._volume = volume
        self._fillna = fillna
        self._run()

    def _run(self):
        vpt = (self._volume * ((self._close - self._close.shift(1, fill_value=self._close.mean()))
                               / self._close.shift(1, fill_value=self._close.mean())))
        self._vpt = vpt.shift(1, fill_value=vpt.mean()) + vpt

    def volume_price_trend(self) -> pd.Series:
        """Volume-price trend (VPT)

        Returns:
            pandas.Series: New feature generated.
        """
        vpt = self._check_fillna(self._vpt, value=0)
        return pd.Series(vpt, name='vpt')


class NegativeVolumeIndexIndicator(IndicatorMixin):
    """Negative Volume Index (NVI)

    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:negative_volume_inde

    Args:
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        fillna(bool): if True, fill nan values with 1000.
    """

    def __init__(self, close: pd.Series, volume: pd.Series, fillna: bool = False):
        self._close = close
        self._volume = volume
        self._fillna = fillna
        self._run()

    def _run(self):
        price_change = self._close.pct_change()
        vol_decrease = (self._volume.shift(1) > self._volume)
        self._nvi = pd.Series(data=np.nan, index=self._close.index, dtype='float64', name='nvi')
        self._nvi.iloc[0] = 1000
        for i in range(1, len(self._nvi)):
            if vol_decrease.iloc[i]:
                self._nvi.iloc[i] = self._nvi.iloc[i - 1] * (1.0 + price_change.iloc[i])
            else:
                self._nvi.iloc[i] = self._nvi.iloc[i - 1]

    def negative_volume_index(self) -> pd.Series:
        """Negative Volume Index (NVI)

        Returns:
            pandas.Series: New feature generated.
        """
        # IDEA: There shouldn't be any na; might be better to throw exception
        nvi = self._check_fillna(self._nvi, value=1000)
        return pd.Series(nvi, name='nvi')


class MFIIndicator(IndicatorMixin):
    """Money Flow Index (MFI)

    Uses both price and volume to measure buying and selling pressure. It is
    positive when the typical price rises (buying pressure) and negative when
    the typical price declines (selling pressure). A ratio of positive and
    negative money flow is then plugged into an RSI formula to create an
    oscillator that moves between zero and one hundred.

    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:money_flow_index_mfi

    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        n(int): n period.
        fillna(bool): if True, fill nan values.
    """

    def __init__(self,
                 high: pd.Series,
                 low: pd.Series,
                 close: pd.Series,
                 volume: pd.Series,
                 n: int = 14,
                 fillna: bool = False):
        self._high = high
        self._low = low
        self._close = close
        self._volume = volume
        self._n = n
        self._fillna = fillna
        self._run()

    def _run(self):
        # 1 typical price
        tp = (self._high + self._low + self._close) / 3.0

        # 2 up or down column
        up_down = np.where(tp > tp.shift(1), 1, np.where(tp < tp.shift(1), -1, 0))

        # 3 money flow
        mf = tp * self._volume * up_down

        # 4 positive and negative money flow with n periods
        n_positive_mf = mf.rolling(self._n).apply(lambda x: np.sum(np.where(x >= 0.0, x, 0.0)), raw=True)
        n_negative_mf = abs(mf.rolling(self._n).apply(lambda x: np.sum(np.where(x < 0.0, x, 0.0)), raw=True))

        # n_positive_mf = np.where(mf.rolling(self._n).sum() >= 0.0, mf, 0.0)
        # n_negative_mf = abs(np.where(mf.rolling(self._n).sum() < 0.0, mf, 0.0))

        # 5 money flow index
        mr = n_positive_mf / n_negative_mf
        self._mr = (100 - (100 / (1 + mr)))

    def money_flow_index(self) -> pd.Series:
        """Money Flow Index (MFI)

        Returns:
            pandas.Series: New feature generated.
        """
        mr = self._check_fillna(self._mr, value=50)
        return pd.Series(mr, name=f'mfi_{self._n}')


class VolumeWeightedAveragePrice(IndicatorMixin):
    """

    """

    def __init__(self,
                 high: pd.Series,
                 low: pd.Series,
                 close: pd.Series,
                 volume: pd.Series,
                 n: int = 14,
                 fillna: bool = False):
        self._high = high
        self._low = low
        self._close = close
        self._volume = volume
        self._n = n
        self._fillna = fillna
        self._run()

    def _run(self):
        # 1 typical price
        tp = (self._high + self._low + self._close) / 3.0

        # 2 typical price * volume
        pv = (tp * self._volume)

        # 3 total price * volume
        total_pv = pv.rolling(self._n, min_periods=self._n).sum()

        # 4 total volume
        total_volume = self._volume.rolling(self._n, min_periods=self._n).sum()

        self.vwap = total_pv / total_volume

    def money_flow_index(self) -> pd.Series:
        """Money Flow Index (MFI)

        Returns:
            pandas.Series: New feature generated.
        """
        vwap = self._check_fillna(self.vwap)
        return pd.Series(vwap, name=f'vwap_{self._n}')


def acc_dist_index(high, low, close, volume, fillna=False):
    """Accumulation/Distribution Index (ADI)

    Acting as leading indicator of price movements.

    https://en.wikipedia.org/wiki/Accumulation/distribution_index

    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        fillna(bool): if True, fill nan values.

    Returns:
        pandas.Series: New feature generated.
    """
    return AccDistIndexIndicator(high=high, low=low, close=close, volume=volume, fillna=fillna).acc_dist_index()


def on_balance_volume(close, volume, fillna=False):
    """On-balance volume (OBV)

    It relates price and volume in the stock market. OBV is based on a
    cumulative total volume.

    https://en.wikipedia.org/wiki/On-balance_volume

    Args:
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        fillna(bool): if True, fill nan values.

    Returns:
        pandas.Series: New feature generated.
    """
    return OnBalanceVolumeIndicator(close=close, volume=volume, fillna=fillna).on_balance_volume()


def chaikin_money_flow(high, low, close, volume, n=20, fillna=False):
    """Chaikin Money Flow (CMF)

    It measures the amount of Money Flow Volume over a specific period.

    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:chaikin_money_flow_cmf

    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        n(int): n period.
        fillna(bool): if True, fill nan values.

    Returns:
        pandas.Series: New feature generated.
    """
    return ChaikinMoneyFlowIndicator(
        high=high, low=low, close=close, volume=volume, n=n, fillna=fillna).chaikin_money_flow()


def force_index(close, volume, n=13, fillna=False):
    """Force Index (FI)

    It illustrates how strong the actual buying or selling pressure is. High
    positive values mean there is a strong rising trend, and low values signify
    a strong downward trend.

    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:force_index

    Args:
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        n(int): n period.
        fillna(bool): if True, fill nan values.

    Returns:
        pandas.Series: New feature generated.
    """
    return ForceIndexIndicator(close=close, volume=volume, n=n, fillna=fillna).force_index()


def ease_of_movement(high, low, volume, n=14, fillna=False):
    """Ease of movement (EoM, EMV)

    It relate an asset's price change to its volume and is particularly useful
    for assessing the strength of a trend.

    https://en.wikipedia.org/wiki/Ease_of_movement

    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        volume(pandas.Series): dataset 'Volume' column.
        n(int): n period.
        fillna(bool): if True, fill nan values.

    Returns:
        pandas.Series: New feature generated.
    """
    return EaseOfMovementIndicator(
        high=high, low=low, volume=volume, n=n, fillna=fillna).ease_of_movement()


def sma_ease_of_movement(high, low, volume, n=14, fillna=False):
    """Ease of movement (EoM, EMV)

    It relate an asset's price change to its volume and is particularly useful
    for assessing the strength of a trend.

    https://en.wikipedia.org/wiki/Ease_of_movement

    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        volume(pandas.Series): dataset 'Volume' column.
        n(int): n period.
        fillna(bool): if True, fill nan values.

    Returns:
        pandas.Series: New feature generated.
    """
    return EaseOfMovementIndicator(
        high=high, low=low, volume=volume, n=n, fillna=fillna).sma_ease_of_movement()


def volume_price_trend(close, volume, fillna=False):
    """Volume-price trend (VPT)

    Is based on a running cumulative volume that adds or substracts a multiple
    of the percentage change in share price trend and current volume, depending
    upon the investment's upward or downward movements.

    https://en.wikipedia.org/wiki/Volume%E2%80%93price_trend

    Args:
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        fillna(bool): if True, fill nan values.

    Returns:
        pandas.Series: New feature generated.
    """
    return VolumePriceTrendIndicator(close=close, volume=volume, fillna=fillna).volume_price_trend()


def negative_volume_index(close, volume, fillna=False):
    """Negative Volume Index (NVI)

    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:negative_volume_inde

    The Negative Volume Index (NVI) is a cumulative indicator that uses the
    change in volume to decide when the smart money is active. Paul Dysart
    first developed this indicator in the 1930s. [...] Dysart's Negative Volume
    Index works under the assumption that the smart money is active on days
    when volume decreases and the not-so-smart money is active on days when
    volume increases.

    The cumulative NVI line was unchanged when volume increased from one
    period to the other. In other words, nothing was done. Norman Fosback, of
    Stock Market Logic, adjusted the indicator by substituting the percentage
    price change for Net Advances.

    This implementation is the Fosback version.

    If today's volume is less than yesterday's volume then:
        nvi(t) = nvi(t-1) * ( 1 + (close(t) - close(t-1)) / close(t-1) )
    Else
        nvi(t) = nvi(t-1)

    Please note: the "stockcharts.com" example calculation just adds the
    percentange change of price to previous NVI when volumes decline; other
    sources indicate that the same percentage of the previous NVI value should
    be added, which is what is implemented here.

    Args:
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        fillna(bool): if True, fill nan values with 1000.

    Returns:
        pandas.Series: New feature generated.

    See also:
        https://en.wikipedia.org/wiki/Negative_volume_index
    """
    return NegativeVolumeIndexIndicator(close=close, volume=volume, fillna=fillna).negative_volume_index()


def money_flow_index(high, low, close, volume, n=14, fillna=False):
    """Money Flow Index (MFI)

    Uses both price and volume to measure buying and selling pressure. It is
    positive when the typical price rises (buying pressure) and negative when
    the typical price declines (selling pressure). A ratio of positive and
    negative money flow is then plugged into an RSI formula to create an
    oscillator that moves between zero and one hundred.

    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:money_flow_index_mfi

    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        n(int): n period.
        fillna(bool): if True, fill nan values.

    Returns:
        pandas.Series: New feature generated.

    """
    indicator = MFIIndicator(high=high, low=low, close=close, volume=volume, n=n, fillna=fillna)
    return indicator.money_flow_index()


# TODO
def put_call_ratio():
    """Put/Call ratio (PCR)
    https://en.wikipedia.org/wiki/Put/call_ratio
    """
    # TODO
    pass
