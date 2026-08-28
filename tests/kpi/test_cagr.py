from src.analytics.cagr import calculate_cagr, calculate_cagr_with_flag


def test_normal_cagr():
    result = calculate_cagr(100, 121, 2)
    assert round(result, 2) == 10.0


def test_zero_base():
    result, flag = calculate_cagr_with_flag(0, 100, 5)
    assert result is None
    assert flag == "ZERO_BASE"


def test_decline_to_loss():
    result, flag = calculate_cagr_with_flag(100, -20, 5)
    assert result is None
    assert flag == "DECLINE_TO_LOSS"


def test_turnaround():
    result, flag = calculate_cagr_with_flag(-20, 100, 5)
    assert result is None
    assert flag == "TURNAROUND"


def test_both_negative():
    result, flag = calculate_cagr_with_flag(-20, -50, 5)
    assert result is None
    assert flag == "BOTH_NEGATIVE"


def test_insufficient_data():
    result, flag = calculate_cagr_with_flag(100, 150, 5, available_years=3)
    assert result is None
    assert flag == "INSUFFICIENT"


def test_positive_to_positive():
    result, flag = calculate_cagr_with_flag(100, 121, 2)
    assert round(result, 2) == 10.0
    assert flag is None


def test_negative_to_zero():
    result, flag = calculate_cagr_with_flag(-20, 0, 5)
    assert result is None
    assert flag is None


def test_zero_base_takes_priority():
    result, flag = calculate_cagr_with_flag(0, -100, 5)
    assert result is None
    assert flag == "ZERO_BASE"


def test_insufficient_data_takes_priority():
    result, flag = calculate_cagr_with_flag(0, 100, 5, available_years=2)
    assert result is None
    assert flag == "INSUFFICIENT"