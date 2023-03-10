"""
    Модуль для определения класса, который хранит функции вычисления медианы:
                                   - медиана и ДИ для одной выборки (v1);
                                   - медиана и ДИ для независимых выборок (v2);
                                   - медиана и ДИ для зависимых выборок (v3);
    а также функции:
                    - для вывода графиков;
                    - для обработки NA-значений.
"""

from Interfaces import *


class CalcMedianSystem:
    def __init__(self):
        self.__table = []
        self.__mode = "v1"
        self.__columns = [None, None]
        self.__titles = [None, None]
        self.__results = [None, None]
        self.__alpha = '90'
        self.__result_diff = None
        self.calculatorEngine = CalculationMedian()
        self.removerNAEngine = SimpleRemoveEngine()
        self.builderEngine = BuildMedianGraphEngine()

    def get_table(self):
        return self.__table

    def set_table(self, table):
        self.__table = table

    def get_mode(self):
        return self.__mode

    def set_mode(self, mode):
        self.__mode = mode
        match mode:
            case "v1":
                self.calculatorEngine = CalculationMedian()
                self.builderEngine = BuildMedianGraphEngine()
            case "v2":
                self.calculatorEngine = CalculationIndependentMedian()
                self.builderEngine = BuildDiffMedianGraphEngine()
            case "v3":
                self.calculatorEngine = CalculationDependentMedian()
                self.builderEngine = BuildDiffMedianGraphEngine()
            case _:
                print("Calculator or Builder not found")

    def get_alpha(self):
        return self.__alpha

    def set_alpha(self, alpha):
        self.__alpha = alpha

    def set_columns(self, title1, title2):
        if title1:
            self.__columns[0] = self.__table[title1]
            self.__titles[0] = title1
            if title2:
                self.__columns[1] = self.__table[title2]
                self.__titles[1] = title2

    def group_columns(self, keys, factor, column):
        df = self.__table
        self.__columns[0] = df[df[factor] == keys[0]][column]
        self.__titles[0] = f"{factor} {keys[0]} ({column})"
        self.__columns[1] = df[df[factor] == keys[1]][column]
        self.__titles[1] = f"{factor} {keys[1]} ({column})"

    def get_columns(self):
        return self.__columns

    def get_titles(self):
        return self.__titles

    def set_results(self, dict_result, num_column):
        self.__results[num_column] = dict_result

    def set_diff_result(self, dict_result):
        self.__result_diff = dict_result

    def get_results(self):
        return self.__results

    def get_diff_result(self):
        return self.__result_diff

    def clear_columns(self):
        self.__columns = [None, None]
        self.__titles = [None, None]
        self.__results = [None, None]
        self.__result_diff = None

    def set_calc_engine(self, engine: CalculationEngine):
        self.calculatorEngine = engine

    def set_removerNA_engine(self, variation):
        match variation:
            case "v1":
                self.removerNAEngine = SimpleRemoveEngine()
            case "v2":
                self.removerNAEngine = RemoveByMeanEngine()
            case "v3":
                self.removerNAEngine = RemoveByMedianEngine()
            case "v4":
                self.removerNAEngine = RemoveByInterpolationEngine()
            case _:
                print("RemoverNA not found")

    def set_builder_engine(self, engine: BuildGraphsEngine):
        self.builderEngine = engine

    def find_median(self):
        return self.calculatorEngine.find_median(self)

    def remove_na(self):
        self.removerNAEngine.remove_na(self)
        return self.__table

    def output_graphs(self):
        return self.builderEngine.build_graphs(self)
