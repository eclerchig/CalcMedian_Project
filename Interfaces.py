from abc import ABC, abstractmethod
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import statistics
import scipy.stats as sps
import pandas as pd
import math


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
    def find_median(self, median_class,  num_column=None):
        alpha = median_class.get_alpha()
        data = median_class.get_columns[num_column]
        g1 = np.array(data, float)
        g1 = g1[np.logical_not(np.isnan(g1))]
        # Тут ошибка для выборок размером 3 и меньше
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


class CalculationDependentMedian(CalculationEngine):
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


class CalculationIndependentMedian(CalculationEngine):
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


class BuildMedianGraphEngine(BuildGraphsEngine):

    def build_graphs(self, median_class):
        figure_m1 = median_class.to_build_distr(median_class.get_results()[0], median_class.get_titles()[0])
        figure_m2 = median_class.return_nan_figure()
        figure_diff = median_class.return_nan_figure()
        figure_summ = median_class.return_nan_figure()
        return [figure_m1, figure_m2, figure_diff, figure_summ]


class BuildDiffMedianGraphEngine(BuildGraphsEngine):
    def build_graphs(self, median_class):
        title1 = median_class.get_titles()[0]
        title2 = median_class.get_titles()[1]
        figure_m1 = median_class.to_build_distr(median_class.get_results()[0], title1)
        figure_m2 = median_class.to_build_distr(median_class.get_results()[1], title2)
        figure_diff = median_class.to_build_distr(median_class.get_diff_result(), 'Разница медиан \"' + title1 + '\" и \"' + title2 + '\"')
        figure_summ = median_class.to_build_intervals()
        return [figure_m1, figure_m2, figure_diff, figure_summ]
