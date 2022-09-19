import numpy as np
import math
z_values = {'90': 1.28,
            '95': 1.96,
            '98': 2.32,
            '99': 2.57,
            '99,9': 3.29}


def find_moda(data, column1, column2, variation, alpha):
    global result
    if variation == 'v1':
        g1 = np.array(data[column1], float)
        g1 = g1[np.logical_not(np.isnan(g1))]
        up_index = int(np.round(1 + g1.size/2 + (z_values[alpha] * np.sqrt(g1.size)/2)))
        low_index = int(np.round(g1.size / 2 - (z_values[alpha] * np.sqrt(g1.size) / 2)))
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
        k = (g1.size*g2.size)/2-(z_values[alpha]*math.sqrt(g1.size*g2.size*(g1.size+g2.size+1)/12))
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
    elif variation == 'v3': #для зависимых
        g = np.array(data.apply(lambda x: x[column1] - x[column2], axis=1), float)
        #g = np.array(data[column1], float)
        size = sum(range(1, g.size+1, 1))
        row = np.zeros(size)
        k = (g.size * (g.size + 1)) / 4 - (z_values[alpha] * math.sqrt(g.size * (g.size + 1) * (2 * g.size + 1) / 24))
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