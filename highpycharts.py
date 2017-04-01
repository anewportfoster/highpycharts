from __future__ import absolute_import

import pandas as pd
from matplotlib import pyplot as plt

try:
    from highcharts import Highchart, Highstock
except ImportError:
    raise ImportError("Could not import highcharts library.  Install with `` pip install python-highcharts `` ")
from toolz import assoc
from enum import IntEnum


class DefaultRange(IntEnum):
    one_month = 0
    three_month = 1
    six_month = 2
    ytd = 3
    year = 4
    all = 5


class _CommonOptions(object):
    axisFormatDateTime = {
        'type': 'datetime',
        'dateTimeLabelFormats': {
            'millisecond': '%H:%M:%S.%L',
            'second': '%H:%M:%S',
            'minute': '%H:%M',
            'hour': '%H:%M',
            'day': '%e. %b',
            'week': '%e. %b',
            'month': '%b \'%y',
            'year': '%Y'
        },
        'tickmarkPlacement': 'on',
        'title': {
            'enabled': False
        }
    }


def line_chart(data, y_name='', title='Chart Title', range_sel=DefaultRange.three_month, num_decimals=2, legend=True,
               figsize_x=900, figsize_y=700):
    """ Creates a highstock line chart

    Data format: date column must be the index for the dataframe and it must be a timestamp/datetime field

    Parameters
    ----------
    data : dataframe
        data with datetime/timestamp index, columns will be the lines
    y_name : string, optional
        title of y axis
    title : string, optional
        title of chart
    range_sel : int, DefaultRange, optional
    num_decimals : int, optional
        precision of values to be displayed in the tooltip, default = 2
    legend : boolean, optional
        shows legend of all line names when true, no legend when false
    figsize_x : int
    figsize_y : int
    """

    H = Highstock(width=figsize_x, height=figsize_y)

    data = data.copy()

    groups_name = data.columns.tolist()
    data['date_field'] = data.index
    data = data.reset_index(drop=True)

    for name in groups_name:
        data1 = data.loc[:, ('date_field', name)].values.tolist()
        H.add_data_set(data1, 'line', name)

    options = {
        'legend': {
            'enabled': legend
        },
        'rangeSelector': {
            'selected': int(range_sel)
        },

        'title': {
            'text': title,
            'style': {
                'fontSize': '21px'
            }
        },
        'yAxis': {
            'title': {
                'text': y_name,
                'style': {
                    'fontSize': '14px'
                }
            }
        },

        'tooltip': {
            'valueDecimals': num_decimals,
            'xDateFormat': '%A, %b %d, %Y',
            'shared': True,
        },

    }

    H.set_dict_options(options)

    return H


def line_customline(data, plotline_date, y_name='', title='Chart Title', range_sel=DefaultRange.three_month,
                    num_decimals=2, line_text='', legend=True, figsize_x=900, figsize_y=700):
    """ Creates a highstock chart that has a vertical line at a specified date, for showing when an event
        occurred

    Data format: date column must be the index for the dataframe and it must be a timestamp/datetime field

    Parameters
    ----------
    data : dataframe
        data with datetime/timestamp index, columns will be the lines
    plotline_date : 'YYYY-MM-DD', time optional
        string of date when change occurred
    y_name : string, optional
        title of y axis
    title : string, optional
        title of chart
    range_sel : int, DefaultRange optional
        initial time range filter
    num_decimals : int, optional
        precision of values to be displayed in the tooltip, default = 2
    line_text : string, optional
        text displayed on the custom plotline
    legend : boolean, optional
        toggle legend on (True) or off (False)
    figsize_x : int
    figsize_y : int
    """

    H = Highstock(width=figsize_x, height=figsize_y)

    data = data.copy()

    groups_name = data.columns.tolist()
    data['date_field'] = data.index
    data = data.reset_index(drop=True)

    for name in groups_name:
        data1 = data.loc[:, ('date_field', name)].values.tolist()
        H.add_data_set(data1, 'line', name)

    options = {
        'legend': {
            'enabled': legend
        },
        'rangeSelector': {
            'selected': int(range_sel)
        },

        'title': {
            'text': title,
            'style': {
                'fontSize': '21px'
            }
        },
        'xAxis': {
            'plotLines': [{
                'value': pd.Timestamp(plotline_date).asm8.astype("datetime64[ms]").astype("int64"),
                'color': 'black',
                'width': 2,
                'zIndex': 4,
                'label': {
                    'text': line_text
                }
            }]
        },
        'yAxis': {
            'title': {
                'text': y_name,
                'style': {
                    'fontSize': '14px'
                }
            },
        },
        'tooltip': {
            'valueDecimals': num_decimals,
            'xDateFormat': '%A, %b %d, %Y',
            'shared': True,
        },

    }

    H.set_dict_options(options)

    return H


def area_stacked(data, y_name='', title='Chart title', range_sel=DefaultRange.three_month, num_decimals=2,
               legend=True, norm=None, cmap=None, figsize_x=900, figsize_y=700):
    """ Creates a highstock stacked area chart

    Data format: date column must be the index for the dataframe and it must be a timestamp/datetime field

    Parameters
    ----------
    data : dataframe
        data with datetime/timestamp index, columns will be the lines
    y_name : string, optional
        title of y axis
    title : string, optional
        title of chart
    range_sel : int, DefaultRange optional
        initial time range filter
    num_decimals : int, optional
        precision of values to be displayed in the tooltip, default = 2
    legend : boolean, optional
        shows legend of all line names when true, no legend when false
    norm : string?
        should colors be normalized
    cmap : string, optional
        set colormap from matplotlib names
    figsize_x : int
    figsize_y : int
    """

    H = Highstock(width=figsize_x, height=figsize_y)

    data = data.copy()

    groups_name = data.columns.tolist()
    data['date_field'] = data.index
    data = data.reset_index(drop=True)

    if norm is None:
        norm = plt.matplotlib.colors.Normalize
    normInstance = norm(vmin=0, vmax=len(groups_name))
    colormap = plt.cm.get_cmap(cmap or 'RdYlBu')

    default_colors = ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9', '#f15c80', '#e4d354', '#2b908f', '#f45b5b',
                      '#91e8e1'] * 10

    for i, name in enumerate(groups_name):
        if cmap is None:
            color = default_colors[i]
        else:
            color = plt.matplotlib.colors.rgb2hex(colormap(normInstance(i)))
        data1 = data.loc[:, ('date_field', name)].values.tolist()
        H.add_data_set(data1, 'area', name, color=color)

    options = {
        'legend': {
            'enabled': legend
        },
        'rangeSelector': {
            'selected': int(range_sel)
        },
        'title': {
            'text': title,
            'style': {
                'fontSize': '20px'
            }
        },
        'xAxis': _CommonOptions.axisFormatDateTime,
        'yAxis': {
            'title': {
                'text': y_name,
                'style': {
                    'fontSize': '13px'
                }
            },
            'labels': {
                'formatter': 'function () {\
                                    return this.value ;\
                                }'
            }
        },
        'tooltip': {
            'shared': True,
            'xDateFormat': '%A, %b %d, %Y',
            'valueDecimals': num_decimals,
        },
        'plotOptions': {
            'area': {
                'stacking': 'normal',
                'connectNulls': True,
                'lineWidth': 1,
                'marker': {
                    'lineWidth': 1,
                }
            }
        }
    }

    H.set_dict_options(options)

    return H


def area_pct_total(data, y_name='', title='Chart title', range_sel=DefaultRange.three_month, num_decimals=2,
                   legend=True, norm=None, cmap=None, figsize_x=900, figsize_y=700):
    """ Creates a highstock stacked area chart that displays data by percent of total

    Data format: date column must be the index for the dataframe and it must be a timestamp/datetime field

    Parameters
    ----------
    data : dataframe
        data with datetime/timestamp index, columns will be the lines
    y_name : string, optional
        title of y axis
    title : string, optional
        title of chart
    range_sel : int, DefaultRange optional
        initial time range filter
    num_decimals : int, optional
        precision of values to be displayed in the tooltip, default = 2
    legend : boolean, optional
        shows legend of all line names when true, no legend when false
    norm : NoneType
        should colors be normalized
    cmap : string, optional
        set colormap from matplotlib names
    figsize_x : int
    figsize_y : int
    """

    H = Highstock(width=figsize_x, height=figsize_y)

    groups_name = data.columns.tolist()

    data = data.copy()

    data['date_field'] = data.index
    data = data.reset_index(drop=True)

    if norm is None:
        norm = plt.matplotlib.colors.Normalize
    normInstance = norm(vmin=0, vmax=len(groups_name))
    colormap = plt.cm.get_cmap(cmap or 'RdYlBu')

    default_colors = ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9',
                      '#f15c80', '#e4d354', '#2b908f', '#f45b5b', '#91e8e1'] * 10

    for i, name in enumerate(groups_name):
        if cmap is None:
            color = default_colors[i]
        else:
            color = plt.matplotlib.colors.rgb2hex(colormap(normInstance(i)))
        data1 = data.loc[:, ('date_field', name)].values.tolist()
        H.add_data_set(data1, 'area', name, color=color)

    options = {
        'legend': {
            'enabled': legend
        },
        'rangeSelector': {
            'selected': int(range_sel)
        },
        'title': {
            'text': title,
            'style': {
                'fontSize': '20px'
            }
        },
        'xAxis': _CommonOptions.axisFormatDateTime,
        'yAxis': {
            'title': {
                'text': 'Percent of ' + y_name,
                'style': {
                    'fontSize': '13px'
                }
            },
            'labels': {
                'formatter': 'function () {\
                                    return this.value ;\
                                }'
            }
        },
        'tooltip': {
            'shared': True,
            'pointFormat': '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.2f}%)<br/>',
            'valueDecimals': num_decimals,
        },
        'plotOptions': {
            'area': {
                'stacking': 'percent',
                'connectNulls': True,
                'lineWidth': 1,
                'marker': {
                    'lineWidth': 1,
                }
            }
        }
    }

    H.set_dict_options(options)

    return H


def line_secondary_y(data, data2, secondy_axis_name, y_name, title='Chart title',
                     range_sel=DefaultRange.three_month, num_decimals=2, figsize_x=900, figsize_y=700):
    """ Creates a highstock line chart with a secondary axis

    Data format: date column must be the index for the dataframe and it must be a timestamp/datetime field

    Parameters
    ----------
    data : dataframe
        data with datetime/timestamp index, columns will be the lines
    data2 : dataframe
        data for the secondary axis, with datetime/timestamp index, columns will be the lines
    secondy_axis_name: string
        title for second y axis
    y_name : string, optional
        title of y axis
    title : string, optional
        title of chart
    range_sel : int, DefaultRange optional
        initial time range filter
    num_decimals : int, optional
        precision of values to be displayed in the tooltip, default = 2
    figsize_x : int
    figsize_y : int
    """

    H = Highstock(width=figsize_x, height=figsize_y)

    data = data.copy()
    data2 = data2.copy()

    groups_name = data.columns.tolist()
    groups_name2 = data2.columns.tolist()

    data['date_field'] = data.index
    data = data.reset_index(drop=True)

    data2['date_field'] = data2.index
    data2 = data2.reset_index()

    for name in groups_name:
        data1 = data.loc[:, ('date_field', name)].values.tolist()
        H.add_data_set(data1, 'line', name)

    for name in groups_name2:
        data3 = data2.loc[:, ('date_field', name)].values.tolist()
        H.add_data_set(data3, 'line', name, yAxis=1)

    options = {
        'legend': {
            'enabled': True
        },
        'rangeSelector': {
            'selected': int(range_sel)
        },

        'title': {
            'text': title,
            'style': {
                'fontSize': '23px'
            }
        },
        'yAxis': [{
            'title': {
                'text': y_name,
                'style': {
                    'fontSize': '14px'
                }
            }
        }, {
            'title': {
                'text': secondy_axis_name,
                'style': {
                    'fontSize': '14px'
                }
            },
            'opposite': False
        }],

        'tooltip': {
            'valueDecimals': num_decimals,
            'xDateFormat': '%A, %b %d, %Y',
            'shared': True,
        },

    }

    H.set_dict_options(options)

    return H


def boxplot(data, y_name, title, num_decimals, x_name='Date', figsize_x=900, figsize_y=700):
    """ Creates a highcharts boxplot

    Data format: dataframe must have index and two columns, 1: date field, 2: values column

    Parameters
    ----------
    data : dataframe
        data with index and two columns: 1 - date field, 2 - values column
    y_name : string, optional
        title of y axis
    title : string, optional
        title of chart
    num_decimals : int, optional
        precision of values to be displayed in the tooltip, default = 2
    x_name: string, optional
        title of x axis
    figsize_x : int
    figsize_y : int
    """

    H = Highchart(width=figsize_x, height=figsize_y)

    data = data.copy()

    data.columns = ['date_field', 'column_1']
    data = data.sort_values('column_1')

    mean = round(data.column_1.mean(), num_decimals)

    data_box_quant = data.groupby('date_field').count()
    for i in range(0, 125, 25):
        data_box_quant['quantile_' + str(i)] = data.groupby('date_field').column_1.quantile(i / 100.0)

    data_box_quant = data_box_quant.reset_index()

    data_box_list = data_box_quant[['date_field', 'quantile_0', 'quantile_25',
                                    'quantile_50', 'quantile_75', 'quantile_100']].values.tolist()

    H.add_data_set(data_box_list, 'boxplot', y_name, tooltip={
        'headerFormat': '<em>Date {point.key}</em><br/>'})

    options = {
        'chart': {
            'type': 'boxplot'
        },
        'title': {
            'text': title
        },
        'legend': {
            'enabled': False
        },
        'xAxis': assoc(_CommonOptions.axisFormatDateTime, 'title', {'text': x_name}),
        'yAxis': {
            'title': {
                'text': y_name
            },
            'plotLines': [{
                'value': mean,
                'color': 'red',
                'width': 1,
                'zIndex': 4,
                'label': {
                    'text': 'Mean: %s  ' % mean,
                    'align': 'right',
                    'style': {
                        'color': 'gray',
                        'plotOptions': {
                            'series': {
                                'dataLabels': {
                                    'enabled': True,
                                    'crop': False,
                                    'overflow': 'none'
                                }
                            }
                        }
                    }
                }
            }]
        },
        'tooltip': {
            'valueDecimals': num_decimals,
            'xDateFormat': '%A, %b %d, %Y',
            'shared': True
        },
    }

    H.set_dict_options(options)

    return H


def line_pct_change(data, y_name='', title='Chart title', range_sel=DefaultRange.three_month, num_decimals=2,
                    legend=True, figsize_x=900, figsize_y=700):
    """ Creates a highstock line percent change chart

    Data format: date column must be the index for the dataframe and it must be a timestamp/datetime field

    Parameters
    ----------
    data : dataframe
        data with index and two columns, 1: date field, 2: values column
    y_name : string, optional
        title of y axis
    title : string, optional
        title of chart
    num_decimals : int, optional
        precision of values to be displayed in the tooltip, default = 2
    range_sel : int, DefaultRange, optional
    num_decimals : int
        precision of values displayed on tooltip
    legend : boolean
        toggles legend on/off
    figsize_x : int
    figsize_y : int
    """

    H = Highstock(width=figsize_x, height=figsize_y)

    data = data.copy()

    groups_name = data.columns.tolist()
    data['date_field'] = data.index
    data = data.reset_index(drop=True)

    for name in groups_name:
        data1 = data.loc[:, ('date_field', name)].values.tolist()
        H.add_data_set(data1, 'line', name)

    options = {
        'legend': {
            'enabled': legend
        },
        'rangeSelector': {
            'selected': int(range_sel)
        },
        'title': {
            'text': title
        },
        'yAxis': {
            'title': {
                'text': y_name
            },
            'labels': {
                'formatter': "function () {\
                                return (this.value > 0 ? ' + ' : '') + this.value + '%';\
                            }"
            },
            'plotLines': [{
                'value': 0,
                'width': 2,
                'color': 'silver'
            }]
        },

        'plotOptions': {
            'series': {
                'compare': 'percent'
            }
        },

        'tooltip': {
            'pointFormat': '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.change}%)<br/>',
            'valueDecimals': num_decimals
        },
    }

    H.set_dict_options(options)

    return H
