import matplotlib.pyplot as plt


def plot_script(spec, date_col, val_col):
    plt.figure(figsize=(12, 6))
    plt.gca().invert_yaxis()

    plt.scatter(spec[date_col], spec[val_col], linestyle="solid")
    plt.title("Value vs. Date")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.grid(True)
    plt.xticks(rotation=45)
    y_min = min(spec[val_col])
    y_max = max(spec[val_col])
    plt.yticks([y_min, y_max])

    plt.tight_layout()

    # Show plot
    plt.show()


import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_candelstick(
    spec, date_col=None, open=None, high=None, low=None, close=None, vol=None
):
    date_col = "date_scraped" if date_col is None else date_col
    open = "Open" if open is None else open
    high = "High" if high is None else high
    low = "Low" if low is None else low
    close = "Close" if close is None else close
    vol = "Vol" if vol is None else vol

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=("OHLC", "Volume"),
        row_width=[0.2, 0.7],
    )

    go.Candlestick(
        x=spec[date_col],
        open=spec[open],
        high=spec[high],
        low=spec[low],
        close=spec[close],
    )

    # Plot OHLC on 1st row
    fig.add_trace(
        go.Candlestick(
            x=spec[date_col],
            open=spec[open],
            high=spec[high],
            low=spec[low],
            close=spec[close],
        ),
        row=1,
        col=1,
    )

    # Bar trace for volumes on 2nd row without legend
    fig.add_trace(go.Bar(x=spec[date_col], y=spec[vol], showlegend=False), row=2, col=1)

    # Do not show OHLC's rangeslider plot
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_xaxes(type="category")
    fig.show()
