import math
import pandas as pd
import statistics
import numpy as np
import scipy.stats as sps
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt

z_values = {'90': 1.28,
            '95': 1.96,
            '98': 2.32,
            '99': 2.57,
            '99,9': 3.29}


class CalcMedianSystem:

    def __init__(self):
        self.__table = []
        self.__mode = 0  # 0 - simple median, 1 - independent samples, 2 - dependent samples
        self.__column1 = ""
        self.__column2 = ""
        self.__title1 = ""
        self.__title2 = ""
        self.__results = []

    def get_table(self):
        return self.__table

    def set_table(self, table):
        self.__table = table

    def get_mode(self):
        return self.__mode

    def set_mode(self, mode):
        self.__mode = mode

    def set_columns(self, title1, title2):
        self.__column1 = self.__table[title1]
        self.__column2 = self.__table[title2]
        self.__title1 = title1
        self.__title2 = title2

    def clear_result(self):
        self.__results = []

    def find_moda(self, data, column1, column2, variation, alpha):
        if self.__mode == 0:
            g1 = np.array(self.__column1, float)
            g1 = g1[np.logical_not(np.isnan(g1))]
            up_index = int(np.round(1 + g1.size / 2 + (z_values[alpha] * np.sqrt(g1.size) / 2)))
            low_index = int(np.round(g1.size / 2 - (z_values[alpha] * np.sqrt(g1.size) / 2)))
            g1.sort()
            low = g1[low_index]
            up = g1[up_index]
            median = np.median(g1)
            self.__results.append(dict(column=self.__title1, data=g1, up=up, low=low, median=median))
        elif self.__mode == 1:  # для независимых выборок
            g1 = np.array(self.__column1, float)
            g2 = np.array(self.__column2, float)
            g1 = g1[np.logical_not(np.isnan(g1))]
            g2 = g2[np.logical_not(np.isnan(g2))]
            row = np.zeros(g1.size * g2.size)  # заполнение 0 массива размером g1*g2
            k = (g1.size * g2.size) / 2 - (
                        z_values[alpha] * math.sqrt(g1.size * g2.size * (g1.size + g2.size + 1) / 12))
            count = 0
            for i in range(g2.size):
                for j in range(g1.size):
                    row[count] = g1[j] - g2[i]
                    count += 1
            row[::-1].sort()
            low = row[count - round(k)]
            up = row[round(k) - 1]
            median = np.median(row)
            self.__results.append(dict(column=[self.__title1, self.__title2], data=row, up=up, low=low, median=median))
        elif self.__mode == 2:
            g = np.array(self.__column1, float)
            size = 0
            for i in range(g.size):
                size += g.size - i
            row = np.zeros(size)
            k = (g.size * (g.size + 1)) / 4 - (
                        z_values[alpha] * math.sqrt(g.size * (g.size + 1) * (2 * g.size + 1) / 24))
            count = 0
            for i in range(g.size):
                for j in range(i, g.size):
                    row[count] = (g[j] + g[i]) / 2
                    count += 1
            row[::-1].sort()
            low = row[count - round(k)]
            up = row[round(k) - 1]
            median = np.median(row)
            self.__results.append(dict(column=[self.__title1, self.__title2], data=row, up=up, low=low, median=median))
        return self.__results

    def remove_na(self, mode):
        #mode: 0 - удалить все NA, 1 - замена средним, 2 - замена медианой, 3 - использование интерполяции
        #df = pd.DataFrame.from_dict(data)
        #columns = list(pd.DataFrame.from_dict(columns)['name']) -----вынести за пределы класса
        df = self.__table
        if mode == 'v1':
            self.__table = self.__table.dropna()
        elif mode == 'v2':
            for col in df.columns:
                df[col].fillna(df[col].mean(), inplace=True)
            self.__table = df
        elif mode == 'v3':
            for col in df.columns:
                median = statistics.median(df[col])
                df[col].fillna(median, inplace=True)
            self.__table = df
        elif mode == 'v4':
            self.__table = df.interpolate(method="linear")
        return self.__table

    plt.style.use('seaborn-whitegrid')

    def to_build_distr(self, variation):
        data = self.__result
        median = data['median']
        low = data['low']
        up = data['up']
        std = data['data'].std()
        mean = data['data'].mean()
        x = np.arange(data['median'] - 3 * std, data['median'] + 3 * std, 0.01)
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

        if variation == 'v1':
            title = str(data['column'])
        else:
            title = 'Разница медиан \"' \
                    + str(data['column'][0]) + '\" и \"' \
                    + str(data['column'][1]) + '\"'
        line_distr.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        return line_distr

    def to_build_intervals(self, dicts):
        conf_intervals = go.Figure()
        for idx, d in enumerate(dicts, start=1):
            conf_intervals = self.to_build_interval(d['median'], d['low'], d['up'], d['column'], idx, conf_intervals)
        conf_intervals.update_layout(
            title={
                'text': 'Изображение доверительных интервалов',
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        return conf_intervals

    def to_build_interval(median, err_low, err_up, column, num, figure):
        tail = 0.2
        if not (isinstance(column, list)):
            name = "ДИ медианы " + column
        else:
            name = "ДИ разницы медиан"
        x = np.array([median, err_up, err_up, err_up, err_up, err_low, err_low, err_low])
        y = np.array([num, num, num + 0.5 * tail, num - 0.5 * tail, num, num, num + 0.5 * tail, num - 0.5 * tail])
        figure.add_trace(go.Scatter(x=x, y=y, name=name, marker=None))
        return figure

    def return_nan_figure(self):
        return go.Figure()