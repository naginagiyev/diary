def parseProductivity(text):
    text = text.strip()
    parts = text.split("/")
    if len(parts) != 2:
        return None
    try:
        numerator = float(parts[0])
        denominator = float(parts[1])
        if denominator == 0:
            return None
        return round((numerator / denominator) * 100)
    except ValueError:
        return None