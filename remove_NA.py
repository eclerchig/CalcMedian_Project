import pandas as pd
import statistics


def execute(dict_data, dict_columns, variation):
    df = pd.DataFrame.from_dict(dict_data)
    columns = list(pd.DataFrame.from_dict(dict_columns)['name'])
    if variation == 'v1':
        result = df.dropna()
        print("ого")
    elif variation == 'v2':
        for col in columns:
            df[col].fillna(df[col].mean(), inplace=True)
        result = df
    elif variation == 'v3':
        for col in columns:
            median = statistics.median(df[col])
            df[col].fillna(median, inplace=True)
        result = df
    elif variation == 'v4':
        result = df.interpolate(method="linear")
    return result
