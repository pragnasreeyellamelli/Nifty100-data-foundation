def normalize_ticker(ticker):
    """Normalize a company ticker/ID."""
    if ticker is None:
        return None

    return str(ticker).strip().upper()
def normalize_year(year):
    """Normalize a financial year/date value to YYYY-MM format."""
    if year is None:
        return None

    value = str(year).strip()

    # Convert formats such as Mar-23 → 2023-03
    if "-" in value:
        parts = value.split("-")

        if len(parts) == 2:
            month, year_part = parts

            month_map = {
                "JAN": "01",
                "FEB": "02",
                "MAR": "03",
                "APR": "04",
                "MAY": "05",
                "JUN": "06",
                "JUL": "07",
                "AUG": "08",
                "SEP": "09",
                "OCT": "10",
                "NOV": "11",
                "DEC": "12",
            }

            month_number = month_map.get(month.upper())

            if month_number and year_part.isdigit():
                year_number = int(year_part)

                if year_number < 100:
                    year_number += 2000

                return f"{year_number:04d}-{month_number}"

    return value