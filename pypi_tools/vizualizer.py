import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt


def create_linear_plot(start_date, downloads):
    days_count = len(downloads)
    print(start_date)
    df = pd.DataFrame(pd.date_range(start_date - timedelta(days=days_count-1), start_date).rename('date'))
    df['downloads'] = downloads
    freq = 'D'
    """#if days_count > 31:
        freq = 'M'
    elif days_count > 7:
        freq = 'W'"""
    df = df.groupby(pd.Grouper(key='date', freq=freq))['downloads'].sum()
    df.index = df.index + pd.DateOffset()

    fig, ax = plt.subplots()
    ax.plot(df.index, df, label='Downloads of {package_name}', color='#31c487')
    ax.set_xticks(df.index)
    ax.set_xticklabels([el.strftime('%Y-%m-%d') for el in df.index])
    ylabels = []
    plt.xticks(rotation=15)
    for t in list(ax.get_yticks()):
        ylabels.append("{:,.0f}".format(t))
    ax.set_yticklabels(ylabels)
    return plt


def save_plot_to_temp_file(plt, file_name):
    plt.savefig(file_name)

def generate_graph(start_date, downloads, file_name):
    plt = create_linear_plot(start_date, downloads)
    save_plot_to_temp_file(plt, file_name)
    return file_name