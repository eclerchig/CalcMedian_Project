import pandas as pd
import numpy as np
import math

def find_moda(data, column1, column2, variation):
    global result
    if variation == 'v1':
        g1 = np.array(data[column1], float)
        g1 = g1[np.logical_not(np.isnan(g1))]
        up_index = int(np.round(1 + g1.size/2 + (1.96 * np.sqrt(g1.size)/2)))
        low_index = int(np.round(g1.size / 2 - (1.96 * np.sqrt(g1.size) / 2)))
        g1.sort()
        low = g1[low_index]
        up = g1[up_index]
        median = np.median(g1)
        result = dict(column=column1, data=g1, up=up, low=low, median=median)
    elif variation == 'v2': #для независимых выборок
        g1 = np.array(data[column1], float)
        g2 = np.array(data[column2], float)
        g1 = g1[np.logical_not(np.isnan(g1))]
        g2 = g2[np.logical_not(np.isnan(g2))]
        row = np.zeros(g1.size*g2.size) #заполнение 0 массива размером g1*g2
        k = (g1.size*g2.size)/2-(1.96*math.sqrt(g1.size*g2.size*(g1.size+g2.size+1)/12))
        count = 0
        for i in range(g2.size):
            for j in range(g1.size):
                row[count] = g1[j] - g2[i]
                count += 1
        row[::-1].sort()
        low = row[count - round(k)]
        up = row[round(k) - 1]
        median = np.median(row)
        result = dict(column=[column1, column2], data=row, up=up, low=low, median=median)
    elif variation == 'v3':
        g = np.array(data[column1], float)
        size = 0
        for i in range(g.size):
            size += g.size - i
        row = np.zeros(size)
        k = (g.size * (g.size + 1)) / 4 - (1.96 * math.sqrt(g.size * (g.size + 1) * (2 * g.size + 1) / 24))
        count = 0
        for i in range(g.size):
            for j in range(i, g.size):
                row[count] = (g[j] + g[i]) / 2
                count += 1
        row[::-1].sort()
        low = row[count - round(k)]
        up = row[round(k) - 1]
        median = np.median(row)
        result = dict(column=[column1, column2], data=row, up=up, low=low, median=median)
    return result