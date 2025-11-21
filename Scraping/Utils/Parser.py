import re

def parse_number(text):
    """Convert numbers like '3.8K' to 3800 and '1.2M' to 1200000"""
    if not text:
        return 0

    text = text.replace(',', '').upper()

    multipliers = {
        'K': 1000,
        'M': 1000000,
        'B': 1000000000
    }

    match = re.match(r'^(\d+\.?\d*)([KMB]?)$', text)
    if match:
        number = float(match.group(1))
        if match.group(2):
            number *= multipliers[match.group(2)]
        return int(number)

    try:
        return int(text)
    except ValueError:
        return 0

