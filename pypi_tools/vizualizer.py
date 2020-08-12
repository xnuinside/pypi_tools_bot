import os
from datetime import datetime, timedelta
import pandas as pd
from random import choice
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
    color = choice(['#31c487', '#f26638', '#bd870b', '#a2bd0b', 
        '#0bbd5b', '#0bbda2', '#0babbd', '#0b7fbd', '#0b43bd',
        '#400bbd', '#610bbd', '#bd0b55'])
    ax.plot(df.index, df, label='Downloads of {package_name}', color=color)
    ax.set_xticks(df.index)
    ax.set_xticklabels([el.strftime('%Y-%m-%d') for el in df.index])
    ylabels = []
    plt.xticks(rotation=15)
    for t in list(ax.get_yticks()):
        ylabels.append("{:,.0f}".format(t))
    ax.set_yticklabels(ylabels)
    return plt


def generate_graph(start_date, downloads, file_name):
    """ generate graph and save it to the file """
    plt = create_linear_plot(start_date, downloads)
    plt.savefig(file_name)
    return file_name