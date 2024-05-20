from datetime import datetime, timedelta

def generate_date_list(start_date_str, end_date_str, exclude_days=['Friday', 'Saturday']):
    # Convert start and end date strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # Initialize an empty list to store dates
    date_list = []

    # Iterate through dates from start to end, adding each date to the list
    current_date = start_date
    while current_date <= end_date:
        if current_date.strftime('%A') not in exclude_days:
            date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return date_list