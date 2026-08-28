def calculate_cagr(start_value, end_value, years):
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Formula:
        ((End / Start) ^ (1 / Years) - 1) * 100

    Returns None when the base value is zero,
    the number of years is zero/negative,
    or the start/end values are not both positive.
    """
    if start_value <= 0 or end_value <= 0 or years <= 0:
        return None

    return ((end_value / start_value) ** (1 / years) - 1) * 100

def calculate_cagr_with_flag(start_value, end_value, years, available_years=None):
    """
    Calculate CAGR and return the appropriate edge-case flag.

    Returns:
        (cagr_value, flag)
    """

    # Not enough historical data
    if available_years is not None and available_years < years:
        return None, "INSUFFICIENT"

    # Zero starting value
    if start_value == 0:
        return None, "ZERO_BASE"

    # Positive to positive: normal CAGR
    if start_value > 0 and end_value > 0:
        return calculate_cagr(start_value, end_value, years), None

    # Positive to negative: decline into loss
    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    # Negative to positive: turnaround
    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    # Negative to negative
    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    # Any remaining case, such as ending at zero
    return None, None