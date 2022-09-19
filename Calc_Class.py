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
        self.__mode = "v1"  # v1 - simple median, v2 - independent samples, v3 - dependent samples
        self.__columns = [None, None]
        self.__titles = [None, None]
        #self.__column1 = None
        #self.__column2 = None
        #self.__title1 = None
        #self.__title2 = None
        self.__results = [None, None]
        self.__alpha = '90'
        #self.__median1 = {'value': None, 'up': None, 'low': None}
        #self.__median2 = {'value': None, 'up': None, 'low': None}
        self.__result_diff = None

    def get_table(self):
        return self.__table

    def set_table(self, table):
        self.__table = table

    def get_mode(self):
        return self.__mode

    def set_mode(self, mode):
        self.__mode = mode

    def get_alpha(self):
        return self.__alpha

    def set_alpha(self, alpha):
        self.__alpha = alpha

    def set_columns(self, title1, title2):
        self.__columns[0] = self.__table[title1]
        self.__titles[0] = title1
        if title2 is not None:
            self.__columns[1] = self.__table[title2]
            self.__titles[1] = title2

    def grouped_columns(self, keys, factor, column):
        df = self.__table
        self.__columns[0] = df[df[factor] == keys[0]][column]
        self.__titles[0] = f"{factor} {keys[0]} ({column})"
        self.__columns[1] = df[df[factor] == keys[1]][column]
        self.__titles[1] = f"{factor} {keys[1]} ({column})"

    def get_columns(self):
        return self.__columns

    def get_titles(self):
        return self.__titles

    def get_results(self):
        return self.__results

    def get_diff_result(self):
        return self.__result_diff

    def clear_columns(self):
        self.__columns = [None, None]
        self.__titles = [None, None]
        self.__results = [None, None]
        self.__result_diff = None


    def find_moda(self, num_column=None):
        if num_column is not None:
            g1 = np.array(self.__columns[num_column], float)
            g1 = g1[np.logical_not(np.isnan(g1))]
            #Тут ошибка для выборок размером 3 и меньше
            up_index = int(np.round(1 + g1.size / 2 + (z_values[self.__alpha] * np.sqrt(g1.size) / 2)))
            low_index = int(np.round(g1.size / 2 - (z_values[self.__alpha] * np.sqrt(g1.size) / 2)))
            g1.sort()
            if (g1.size < up_index) or (low_index < 0):
                return "error"
            self.__results[num_column] = {'median': np.median(g1), 'up': g1[up_index-1], 'low': g1[low_index-1]}
            result = self.__results[num_column]
        elif self.__mode == 'v2':  # для независимых выборок
            g1 = np.array(self.__columns[0], float)
            g2 = np.array(self.__columns[1], float)
            g1 = g1[np.logical_not(np.isnan(g1))]
            g2 = g2[np.logical_not(np.isnan(g2))]
            row = np.zeros(g1.size * g2.size)  # заполнение 0 массива размером g1*g2
            k = (g1.size * g2.size) / 2 - (
                        z_values[self.__alpha] * math.sqrt(g1.size * g2.size * (g1.size + g2.size + 1) / 12))
            count = 0
            for i in range(g2.size):
                for j in range(g1.size):
                    row[count] = g1[j] - g2[i]
                    count += 1
            row.sort()
            if (count < round(k)) or ((count - round(k)) < 0) or (k < 0.5):
                return "error"
            self.__result_diff = {'median': np.median(row), 'up': row[count - round(k)], 'low': row[round(k) - 1], 'data': row}
            result = self.__result_diff
            #self.__results.append(dict(column=[self.__title1, self.__title2], data=row, up=up, low=low, median=median))
        elif self.__mode == 'v3':
            g = np.array(self.__table.apply(lambda x: x[self.__titles[0]] - x[self.__titles[1]], axis=1), float)
            #g = np.array(self.__table[self.__titles[0]], float)
            g = g[np.logical_not(np.isnan(g))]
            size = sum(range(1, g.size + 1, 1))
            row = np.zeros(size)
            k = (g.size * (g.size + 1)) / 4 - (
                        z_values[self.__alpha] * math.sqrt(g.size * (g.size + 1) * (2 * g.size + 1) / 24))
            count = 0
            for i in range(g.size):
                for j in range(i, g.size):
                    row[count] = (g[j] + g[i]) / 2
                    count += 1
            row.sort()
            if (count < round(k)) or ((count - round(k)) < 0):
                return "error"
            self.__result_diff = {'median': np.median(row), 'up': row[count - round(k)], 'low': row[round(k) - 1], 'data': row}
            result = self.__result_diff
        return result

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

    def to_build_intervals(self):
        conf_intervals = go.Figure()
        median1 = self.__results[0]
        median2 = self.__results[1]
        conf_intervals = self.to_build_interval(median1['median'], median1['low'], median1['up'], self.__titles[0], 1,
                                                conf_intervals)
        conf_intervals = self.to_build_interval(median2['median'], median2['low'], median2['up'], self.__titles[1], 2,
                                                conf_intervals)
        median_diff = self.__result_diff
        conf_intervals = self.to_build_interval(median_diff['median'], median_diff['low'], median_diff['up'],
                                           self.__titles, 3, conf_intervals)
        conf_intervals.update_layout(
            title={
                'text': 'Изображение доверительных интервалов',
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        return conf_intervals

    def to_build_interval(self, median, err_low, err_up, column, num, figure):
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