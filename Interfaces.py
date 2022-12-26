from abc import ABC, abstractmethod
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import statistics
import scipy.stats as sps
import pandas as pd
import math

import calc_median


class CalculationEngine(ABC):
    Z_VALUES = {'90': 1.28,
                '95': 1.96,
                '98': 2.32,
                '99': 2.57,
                '99,9': 3.29}

    @abstractmethod
    def find_median(self, median_class, num_column=None):
        pass


class CalculationMedian(CalculationEngine):
    def find_median(self, median_class, num_column=0):
        alpha = median_class.get_alpha()
        data = median_class.get_columns()[num_column]
        g1 = np.array(data, float)
        g1 = g1[np.logical_not(np.isnan(g1))]
        up_index = int(np.round(1 + g1.size / 2 + (self.Z_VALUES[alpha] * np.sqrt(g1.size) / 2)))
        low_index = int(np.round(g1.size / 2 - (self.Z_VALUES[alpha] * np.sqrt(g1.size) / 2)))
        g1.sort()
        if (g1.size < up_index) or (low_index < 0):
            return "error"
        median_class.set_results({'median': np.median(g1),
                                  'up': g1[up_index - 1],
                                  'low': g1[low_index - 1],
                                  'data': g1},
                                 num_column)
        return median_class.get_results()


class CalculationDependentMedian(CalculationEngine):

    def __init__(self):
        self.__calc_median = CalculationMedian()

    def find_median(self, median_class, num_column=None):
        titles = median_class.get_titles()
        table = median_class.get_table()
        alpha = median_class.get_alpha()
        g = np.array(table.apply(lambda x: x[titles[0]] - x[titles[1]], axis=1), float)
        g = g[np.logical_not(np.isnan(g))]
        size = sum(range(1, g.size + 1, 1))
        row = np.zeros(size)
        k = (g.size * (g.size + 1)) / 4 - (
                self.Z_VALUES[alpha] * math.sqrt(g.size * (g.size + 1) * (2 * g.size + 1) / 24))
        count = 0
        for i in range(g.size):
            for j in range(i, g.size):
                row[count] = (g[j] + g[i]) / 2
                count += 1
        row.sort()
        if (count < round(k)) or ((count - round(k)) < 0):
            return "error"
        median_class.set_diff_result({'median': np.median(row),
                                      'up': row[count - round(k)],
                                      'low': row[round(k) - 1],
                                      'data': row})
        return [self.__calc_median.find_median(median_class, 0), self.__calc_median.find_median(median_class, 1),
                median_class.get_diff_result()]


class CalculationIndependentMedian(CalculationEngine):
    def __init__(self):
        self.__calc_median = CalculationMedian()

    def find_median(self, median_class, num_column=None):
        columns = median_class.get_columns()
        alpha = median_class.get_alpha()
        g1 = np.array(columns[0], float)
        g2 = np.array(columns[1], float)
        g1 = g1[np.logical_not(np.isnan(g1))]
        g2 = g2[np.logical_not(np.isnan(g2))]
        row = np.zeros(g1.size * g2.size)  # заполнение 0 массива размером g1*g2
        k = (g1.size * g2.size) / 2 - (
                self.Z_VALUES[alpha] * math.sqrt(g1.size * g2.size * (g1.size + g2.size + 1) / 12))
        count = 0
        for i in range(g2.size):
            for j in range(g1.size):
                row[count] = g1[j] - g2[i]
                count += 1
        row.sort()
        if (count < round(k)) or ((count - round(k)) < 0) or (k < 0.5):
            return "error"
        median_class.set_diff_result({'median': np.median(row),
                                      'up': row[count - round(k)],
                                      'low': row[round(k) - 1],

                                      'data': row})
        return [self.__calc_median.find_median(median_class, 0), self.__calc_median.find_median(median_class, 1),
                median_class.get_diff_result()]


class RemoveNAEngine(ABC):

    @abstractmethod
    def remove_na(self, median_class):
        pass


class SimpleRemoveEngine(RemoveNAEngine):
    def remove_na(self, median_class):
        table = median_class.get_table()
        median_class.set_table(table.dropna())


class RemoveByMeanEngine(RemoveNAEngine):
    def remove_na(self, median_class):
        table = median_class.get_table()
        for col in table.columns:
            table[col].fillna(table[col].mean(), inplace=True)
        median_class.set_table(table)


class RemoveByMedianEngine(RemoveNAEngine):
    def remove_na(self, median_class):
        table = median_class.get_table()
        for col in table.columns:
            median = statistics.median(table[col])
            table[col].fillna(median, inplace=True)
        median_class.set_table(table)


class RemoveByInterpolationEngine(RemoveNAEngine):
    def remove_na(self, median_class):
        table = median_class.get_table()
        median_class.set_table(table.interpolate(method="linear"))


class BuildGraphsEngine(ABC):
    Z_VALUES = {'90': 1.28,
                '95': 1.96,
                '98': 2.32,
                '99': 2.57,
                '99,9': 3.29}

    @abstractmethod
    def build_graphs(self, median_class) -> list:
        pass

    @staticmethod
    def to_build_distr(data, title):
        median = data['median']
        low = data['low']
        up = data['up']
        std = data['data'].std()
        mean = data['data'].mean()
        x = np.arange(mean - 3 * std, mean + 3 * std, 0.01)
        y = np.array(sps.norm.pdf(x, mean, std))
        df = pd.DataFrame({'x': x, 'y': y})
        line_distr = px.line(df, x="x", y="y", color_discrete_sequence=['darkorange'])
        line_distr.add_traces([
            go.Scatter(
                x=[low, low],
                y=[0, sps.norm.pdf(low, mean, std)],
                line={
                    'color': 'rgb(50, 171, 96)',
                    'width': 2,
                },
                name='Нижняя граница ДИ'
            ),
            go.Scatter(
                x=[up, up],
                y=[0, sps.norm.pdf(up, mean, std)],
                line={
                    'color': 'rgb(50, 171, 96)',
                    'width': 2,
                },
                name='Верхняя граница ДИ'
            ),
            go.Scatter(
                x=[median, median],
                y=[0, sps.norm.pdf(median, mean, std)],
                line={
                    'color': 'rgb(0, 0, 0)',
                    'width': 3,
                    'dash': 'solid'
                },
                name='Медиана'
            ),
            go.Scatter(
                x=[mean, mean],
                y=[0, sps.norm.pdf(mean, mean, std)],
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

        line_distr.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        return line_distr

    @staticmethod
    def to_build_intervals(median1, median2, median_diff, median_class):

        conf_intervals = go.Figure()
        conf_intervals = BuildGraphsEngine.to_build_interval(median1['median'], median1['low'], median1['up'],
                                                             median_class.get_titles()[0], 1, conf_intervals)
        conf_intervals = BuildGraphsEngine.to_build_interval(median2['median'], median2['low'], median2['up'],
                                                             median_class.get_titles()[1], 2, conf_intervals)
        conf_intervals = BuildGraphsEngine.to_build_interval(median_diff['median'], median_diff['low'], median_diff['up'],
                                                             median_class.get_titles(), 3, conf_intervals)
        conf_intervals.update_layout(
            title={
                'text': 'Изображение доверительных интервалов',
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        return conf_intervals

    @staticmethod
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

    @staticmethod
    def return_nan_figure():
        return go.Figure()


class BuildMedianGraphEngine(BuildGraphsEngine):

    def build_graphs(self, median_class):
        figure_m1 = BuildGraphsEngine.to_build_distr(median_class.get_results()[0], median_class.get_titles()[0])
        figure_m2 = BuildGraphsEngine.return_nan_figure()
        figure_diff = BuildGraphsEngine.return_nan_figure()
        conf_intervals = BuildGraphsEngine.return_nan_figure()
        return {'figure_m1': figure_m1,
                'figure_m2': figure_m2,
                'figure_diff': figure_diff,
                'conf_intervals': conf_intervals}


class BuildDiffMedianGraphEngine(BuildGraphsEngine):
    def build_graphs(self, median_class):
        title1 = median_class.get_titles()[0]
        title2 = median_class.get_titles()[1]
        figure_m1 = BuildGraphsEngine.to_build_distr(median_class.get_results()[0], title1)
        figure_m2 = BuildGraphsEngine.to_build_distr(median_class.get_results()[1], title2)
        figure_diff = BuildGraphsEngine.to_build_distr(median_class.get_diff_result(), 'Разница медиан \"' + title1 + '\" и \"' + title2 + '\"')
        conf_intervals = BuildGraphsEngine.to_build_intervals(median_class.get_results()[0], median_class.get_results()[1],
                                                              median_class.get_diff_result(), median_class)
        return {'figure_m1': figure_m1,
                'figure_m2': figure_m2,
                'figure_diff': figure_diff,
                'conf_intervals': conf_intervals}
