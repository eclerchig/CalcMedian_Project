import pandas as pd
import numpy as np
import scipy.stats as sps
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt

plt.style.use('seaborn-whitegrid')


def to_build_distr(result, variation, data, titles):
    median = result['median']
    low = result['low']
    up = result['up']
    std = data.std()
    mean = data.mean()
    x = np.arange(result['median'] - 3 * std, result['median'] + 3 * std, 0.01)
    y = np.array(sps.norm.pdf(x, median, std))
    df = pd.DataFrame({'x': x, 'y': y})
    line_distr = px.line(df, x="x", y="y", color_discrete_sequence=['darkorange'])
    line_distr.add_traces([
        go.Scatter(
            x=[low, low],
            y=[0, sps.norm.pdf(low, median, std)],
            line={
                'color': 'rgb(50, 171, 96)',
                'width': 2,
            },
            name='Нижняя граница ДИ'
        ),
        go.Scatter(
            x=[up, up],
            y=[0, sps.norm.pdf(up, median, std)],
            line={
                'color': 'rgb(50, 171, 96)',
                'width': 2,
            },
            name='Верхняя граница ДИ'
        ),
        go.Scatter(
            x=[median, median],
            y=[0, sps.norm.pdf(median, median, std)],
            line={
                'color': 'rgb(0, 0, 0)',
                'width': 3,
                'dash': 'solid'
            },
            name='Медиана'
        ),
        go.Scatter(
            x=[mean, mean],
            y=[0, sps.norm.pdf(mean, median, std)],
            line={
                'color': 'rgb(255, 43, 43)',
                'width': 2,
                'dash': 'dash'
            },
            name='Среднее'
        ),
    ])
    line_distr.add_vrect(x0=low, x1=up,
                         annotation_text="ДИ", annotation_position="bottom left",
                         fillcolor="green", opacity=0.25, line_width=0)

    if variation != 'v1':
        title = 'Разница медиан \"' \
                + titles[0] + '\" и \"' \
                + titles[1] + '\"'
    else:
        title = titles
    line_distr.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return line_distr


def to_build_intervals(dicts_median, dict_diff_median):
    conf_intervals = go.Figure()
    for idx, d in enumerate(dicts_median, start=1):
        conf_intervals = to_build_interval(d['median'], d['low'], d['up'], d['column'], idx, conf_intervals)
    conf_intervals = to_build_interval(dict_diff_median['median'], dict_diff_median['low'], dict_diff_median['up'], self, idx, conf_intervals)
    conf_intervals.update_layout(
        title={
            'text': 'Изображение доверительных интервалов',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return conf_intervals


def to_build_interval(median, err_low, err_up, column, num, figure):
    tail = 0.2
    if not(isinstance(column, list)):
        name = "ДИ медианы " + column
    else:
        name = "ДИ разницы медиан"
    x = np.array([median, err_up, err_up, err_up, err_up, err_low, err_low, err_low])
    y = np.array([num, num, num + 0.5 * tail, num - 0.5 * tail, num, num, num + 0.5 * tail, num - 0.5 * tail])
    figure.add_trace(go.Scatter(x=x, y=y, name=name, marker=None))
    return figure

def return_nan_figure():
    return go.Figure()