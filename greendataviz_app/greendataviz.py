import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import re
from itertools import chain
from datetime import datetime

_sesh = dict()

def get_listings(file=None):
    if not 'listings' in _sesh.keys():
        df = get_variation_sales_data(file) 
        _sesh['listings'] = df['Item Name'].unique()
        _sesh['df'] = df
    return _sesh['listings']
 
def get_variation_sales_data(file=None):
    """
    Gets relevant data from a variety of sources, such as a csv, or via the API (with
    helper functions. 

    Current methods supported: None; in dev

    Args:
        file (str): filepath to csv such as "./data/EtsySoldOrders2020.csv"
    Returns;
        TODO
    """
    df = None
    if file:
        #read file
        df = pd.read_csv(file)
        #clean data
        df = df[['Sale Date', 'Item Name', 'Quantity', 'Price', 'Variations', 'SKU']]
        df['Sale Date'] = pd.to_datetime(df['Sale Date'])
        df.fillna({'Variations':''}, inplace=True)
        explode_variations_column(df)
    else: #use API
        pass

    return df

def explode_variations_column(df, suffix="", drop=True):
    """
    Uses Variations column (a field of multiple key-value pairs in a string)
    to add a column to the DataFrame for each variation type (size, color, style).

    Args:
        df (DataFrame): contains a Variations column. Will be edited inplace
        suffix (str): suffix to append to the new column names. Default blank
        drop (bool): drops the old Variations column if True. Default True

    Returns:
        (list) newly created column names
    """
    def grab_value(key, string):
        try: 
            result = re.findall(f'{key}:[\w\s]*,?', string)[0]
            result = result[len(key)+1:].strip(',')
        except IndexError:
            result = ""
        return result
    
    keys = pd.Series(chain.from_iterable(
        df.Variations.apply(lambda st: [s.strip(':') for s in re.findall(r'\w*:',st)])
    )).unique()
    
    new_col_names = [k+suffix for k in keys]
    for c in new_col_names:
        df[c] = df.Variations.apply(lambda string: grab_value(c, string))

    if drop:
        df.drop(columns='Variations', inplace=True)

    _sesh['var_col_names'] = new_col_names
    return new_col_names

 def variation_sales_linegraph(df, listing, gb_freq, x_axis_label='Sale Date', y_axis_label='Quantity'):
    #focus only on the requested listing
    plot_df = df[df['Item Name']==listing]
    if not 'Variation' in df.columns:
        plot_df['Variations'] = ""
        for n in _sesh['var_col_names']:
            plot_df.loc[:,'Variations'] += plot_df[n] + ' '
    relevant_variations = plot_df['Variations'].unique()

    plot_df = plot_df.groupby([
        pd.Grouper(key=x_axis_label,freq=gb_freq), 
        "Variations"
    ]).sum().reset_index()

    pt = plot_df.pivot_table(index = x_axis_label, columns='Variations', values=y_axis_label)\
        .fillna(0, downcast='infer')

    #init plot
    fig, ax = plt.subplots(figsize=(14,6))


    for v in relevant_variations:
        ax.plot(pt.index, pt[v], label=v)

    #plot prettying
    plt.xticks(rotation='vertical')
    ax.set_xlabel(x_axis_label)
    ax.set_ylabel(y_axis_label)
    ax.legend()
    
    if not os.path.exists('greendataviz_app/static'):
        os.makedirs('greendataviz_app/static')
    plt_name = datetime.now().strftime(f'%Y-%m-%d-%H_{listing}_{gb_freq}.jpg')
    plt.savefig('./greendataviz_app/static/'+plt_name)

    return plt_name, pt
