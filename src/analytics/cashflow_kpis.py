def free_cash_flow(operating_activity, investing_activity):
    """
    Calculate Free Cash Flow.

    Formula:
        Operating Activity + Investing Activity

    Negative FCF is allowed.
    """
    return operating_activity + investing_activity

def cfo_quality_score(cfo_values, pat_values):
    """
    Calculate the average CFO / PAT ratio over 5 years.

    Classification:
        > 1.0       = High Quality
        0.5 to 1.0  = Moderate
        < 0.5       = Accrual Risk

    Returns (None, None) when PAT is zero for any year.
    """
    if len(cfo_values) != len(pat_values):
        raise ValueError("CFO and PAT values must have the same length")

    ratios = []

    for cfo, pat in zip(cfo_values, pat_values):
        if pat == 0:
            return None, None

        ratios.append(cfo / pat)

    if not ratios:
        return None, None

    average_ratio = sum(ratios) / len(ratios)

    if average_ratio > 1.0:
        quality = "High Quality"
    elif average_ratio >= 0.5:
        quality = "Moderate"
    else:
        quality = "Accrual Risk"

    return average_ratio, quality

def capex_intensity(investing_activity, sales):
    """
    Calculate CapEx Intensity.

    Formula:
        abs(Investing Activity) / Sales * 100

    Classification:
        < 3%       = Asset Light
        3% to 8%   = Moderate
        > 8%       = Capital Intensive

    Returns (None, None) when sales is zero.
    """
    if sales == 0:
        return None, None

    intensity = abs(investing_activity) / sales * 100

    if intensity < 3:
        classification = "Asset Light"
    elif intensity <= 8:
        classification = "Moderate"
    else:
        classification = "Capital Intensive"

    return intensity, classification

def fcf_conversion_rate(fcf, operating_profit):
    """
    Calculate FCF Conversion Rate.

    Formula:
        FCF / Operating Profit * 100

    Returns None when operating profit is zero.
    """
    if operating_profit == 0:
        return None

    return (fcf / operating_profit) * 100

def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=None):
    """
    Classify capital allocation based on the signs of CFO, CFI and CFF.

    Signs:
        + = positive
        - = negative

    The (+,-,-) pattern is classified as:
        Shareholder Returns when CFO/PAT is high,
        otherwise Reinvestor.
    """

    cfo_sign = "+" if cfo > 0 else "-"
    cfi_sign = "+" if cfi > 0 else "-"
    cff_sign = "+" if cff > 0 else "-"

    pattern = (cfo_sign, cfi_sign, cff_sign)

    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"

    if pattern == ("+", "+", "-"):
        return "Liquidating Assets"

    if pattern == ("-", "+", "+"):
        return "Distress Signal"

    if pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if pattern == ("+", "+", "+"):
        return "Cash Accumulator"

    if pattern == ("-", "-", "-"):
        return "Pre-Revenue"

    if pattern == ("+", "-", "+"):
        return "Mixed"

    return "Unknown"