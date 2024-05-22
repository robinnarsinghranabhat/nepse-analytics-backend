from datetime import datetime, timedelta


def generate_date_list(
    start_date_str, end_date_str, exclude_days=["Friday", "Saturday"]
):
    # Convert start and end date strings to datetime objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Initialize an empty list to store dates
    date_list = []

    # Iterate through dates from start to end, adding each date to the list
    current_date = start_date
    while current_date <= end_date:
        if current_date.strftime("%A") not in exclude_days:
            date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    return date_list


def longest_consecutive_dates(date_column: list[datetime]):
    """
    Takes in List of datetimes.
    Returns start and end date without having any gaps
    """
    date_column = sorted(set(date_column))  # Remove duplicates and sort dates
    longest_chain = []
    current_chain = []

    for i in range(1, len(date_column)):
        if (date_column[i] - date_column[i - 1]).days == 1:
            current_chain.append(date_column[i - 1])
            current_chain.append(date_column[i])
        else:
            if len(current_chain) > len(longest_chain):
                longest_chain = current_chain
            current_chain = []

    # Check the last chain
    if len(current_chain) > len(longest_chain):
        longest_chain = current_chain

    if longest_chain:
        start_date = longest_chain[0]
        end_date = longest_chain[-1]
        return start_date, end_date
    else:
        return None, None


def _str_to_int(x):
    """
    Converts numerical string (like 10,999.00) to integer
    """
    try:
        x = float(x.replace(",", ""))
        # x = x/1000
    except Exception:
        print("ERREED while converting : ", x)
        x = -1
    return x
