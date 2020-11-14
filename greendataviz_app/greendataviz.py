import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, sys, re
from itertools import chain
from datetime import datetime

plt.style.use("fivethirtyeight")

_sesh = dict()

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")


def get_listings(file=None):
    if not "listings" in _sesh.keys():
        df = get_variation_sales_data(file)
        _sesh["listings"] = df["Item Name"].unique()
        _sesh["df"] = df
    return _sesh["listings"]


def get_variation_sales_data(file=None, clean_hook_func = None):
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
        # read file
        df = pd.read_csv(file)
        # clean data
        df = df[["Sale Date", "Item Name", "Quantity", "Price", "Variations", "SKU"]]
        df["Sale Date"] = pd.to_datetime(df["Sale Date"])
        df.fillna({"Variations": ""}, inplace=True)
        
        if clean_hook_func:
            clean_hook_func(df)

    else:  # use API
        pass

    return df

def printerror_clean(df):
    SKU_transform = {
        'S W PFP':'W 6 PFP',
        'M W PFP':'W 8 PFP',
        'L W PFP':'W 10 PFP',
        'S S PFP':'S 6 PFP',
        'M S PFP':'S 8 PFP',
        'L S PFP':'S 10 PFP',
        'S B PFP':'B 6 PFP',
        'M B PFP':'B 8 PFP',
        'L B PFP':'B 10 PFP',
        'W PFP 10':'W 10 PFP',
        'S PFP 10':'S 10 PFP',
        'B PFP  10':'B 10 PFP'
    }
    df.SKU = df.SKU.transform(lambda sku: SKU_transform.get(sku, sku))

    row_filter = df.SKU.isna() & (df['Item Name']=='3D Printed Polyface Planter')
    df.loc[row_filter,'SKU'] = df[row_filter].Variations.apply(_fill_SKU_with_variation)
    df["Variations"] = df["Variations"].transform(_stripdelay)
    _explode_variations_column(df)
    #no return - changes in-place

def _stripdelay(s):
    m = re.compile("\([\w\s]+\)\s*").search(s)
    if m:
        return s[: m.span()[0]] + s[m.span()[1] :]
    else:
        return s
def _fill_SKU_with_variation(var):
    var = var.lower()
    size_map = {
        'large': '10',
        '10': '10',
        'medium': '8',
        '8': '8',
        'small': '6',
        '6': '6'
    }
    color_map = {
        'white': 'W',
        'silver': 'S',
        'black': 'B'
    }
    size = color = None
    for k in size_map.keys():
        if k in var:
            size = size_map[k]
            break
    for k in color_map.keys():
        if k in var:
            color = color_map[k]
            break
    return f'{color} {size} PFP'

def _explode_variations_column(df, suffix="", drop=True):
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
            result = re.findall(f"{key}:[\w\s]*,?", string)[0]
            result = result[len(key) + 1 :].strip(",")
        except IndexError:
            result = ""
        return result

    keys = pd.Series(
        chain.from_iterable(
            df.Variations.apply(
                lambda st: [s.strip(":") for s in re.findall(r"\w*:", st)]
            )
        )
    ).unique()

    new_col_names = [k + suffix for k in keys]
    for c in new_col_names:
        df[c] = df.Variations.apply(lambda string: grab_value(c, string))

    if drop:
        df.drop(columns="Variations", inplace=True)

    _sesh["var_col_names"] = new_col_names
    return new_col_names


def variation_sales_linegraph(
    df, listing, gb_freq, x_axis_label="Sale Date", y_axis_label="Quantity"
):
    # focus only on the requested listing
    plot_df = df[df["Item Name"] == listing]
#    if not "Variations" in plot_df.columns:
#        plot_df["Variations"] = ""
#        for n in _sesh["var_col_names"]:
#            plot_df.loc[:, "Variations"] += plot_df[n] + " "
#    relevant_variations = plot_df["Variations"].unique()

    plot_df = (
        plot_df.groupby([pd.Grouper(key=x_axis_label, freq='D'), "SKU"])
        .sum()
        .reset_index()
    )

    plot_df = plot_df[plot_df[x_axis_label] != plot_df[x_axis_label].max()]
    
    plot_df = (
        plot_df.groupby([pd.Grouper(key=x_axis_label, freq=gb_freq), "SKU"])
        .sum()
        .reset_index()
    )

    pt = (
        plot_df.pivot_table(
            index=x_axis_label, columns="SKU", values=y_axis_label
        )
        .fillna(0, downcast="infer")
        .asfreq(gb_freq, fill_value=0)
    )


    return pt
