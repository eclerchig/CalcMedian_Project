import base64
import io
import dash_bootstrap_components as dbc
import dash
import calc_moda
import remove_NA
import graphs

from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from dash.exceptions import PreventUpdate

import pandas as pd
import numpy as np

dbc_css = ("https://codepen.io/chriddyp/pen/bWLwgP.css")
dbc_BTicons = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css"
dbc_AWicons = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css, dbc_AWicons, dbc_BTicons])
df = pd.DataFrame()


def build_table(data):
    return html.Div([
        dash_table.DataTable(
            data.to_dict('records'),
            [{'name': i, 'id': i} for i in data.columns],
            id='table_data'
        )
    ])


def out_error(text):
    return html.P([
        html.B(["Ошибка: "]),
        text
    ],
        style={'color': 'red'})


def build_result(result_clmn1, result_clmn2, result_diff):
    median1 = np.round(result_clmn1['median'], 2)
    low1 = np.round(result_clmn1['low'], 2)
    up1 = np.round(result_clmn1['up'], 2)
    if result_diff is not None:
        median2 = np.round(result_clmn2['median'], 2)
        low2 = np.round(result_clmn2['low'], 2)
        up2 = np.round(result_clmn2['up'], 2)
        return html.Div([
            html.P([html.B("Медиана №1 (столбец \"" + result_clmn1['column'] + "\"): "), str(median1)]),
            html.P([html.B("Нижняя граница: "), str(low1)]),
            html.P([html.B("Верхняя граница: "), str(up1)]),
            html.P([html.B("Представление: "), str(median1) + " 95% ДИ [" + str(low1) + ";" + str(up1) + "]"]),
            html.Br(),
            html.P([html.B("Медиана №2 (столбец \"" + result_clmn2['column'] + "\"): "), str(median2)]),
            html.P([html.B("Нижняя граница: "), str(low2)]),
            html.P([html.B("Верхняя граница: "), str(up2)]),
            html.P([html.B("Представление: "), str(median2) + " 95% ДИ [" + str(low2) + ";" + str(up2) + "]"]),
            html.Br(),
            html.P([html.B("Разница медиан: "), str(np.round(result_diff['median'], 2)) + " 95% ДИ [" +
                    str(np.round(result_diff['low'], 2)) + ";" + str(np.round(result_diff['up'], 2)) + "]"])
        ])
    else:
        return html.Div([
            html.P([html.B("Медиана №1 (столбец \"" + result_clmn1['column'] + "\"): "), str(median1)]),
            html.P([html.B("Нижняя граница: "), str(low1)]),
            html.P([html.B("Верхняя граница: "), str(up1)]),
            html.P([html.B("Представление: "), str(median1) + " 95% ДИ [" + str(low1) + ";" + str(up1) + "]"])
        ])


app.layout = html.Div(
    dbc.Row([
        dbc.Col([
            dbc.Col([
                html.H3(children=[
                    "Загрузка данных \xa0",
                    html.I(className="bi bi-info-circle",
                           id="help-upload",
                           style={'font-size': '2rem'}),
                    dbc.Tooltip(
                        ["Можно загрузить файлы следующих форматов:", html.Br(),
                         ".CSV - при использовании в качестве разделителя столбцов запятой, "
                         "в качестве десятичного разделителя - точки;",
                         html.Br(), ".XLSX, .XLS", html.Br(), "Можно прикрепить только один файл!"
                         ],
                        target="help-upload",
                        placement='bottom',
                        delay={'show': 0,
                               'hide': 50},
                        style={'font-size': '1.5rem'})
                ]),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Перетащите или ',
                        html.A('Выберите файл')
                    ]),
                    style={
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px 0'
                    },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
                html.Div(id='body-error-upload'),
                html.P([
                    "Действия по обработке пропущенных значений \xa0",
                    html.I(className="bi bi-info-circle",
                           id="help-imputn",
                           style={'font-size': '1.5rem'}),
                    dbc.Tooltip(
                        ["Описание каждого действия:", html.Br(),
                         html.B("Убрать все записи с NA значениями:"),
                         " удалить строки при наличии хотя бы одного пропущенного значения;", html.Br(),
                         html.B("Использовать среднее для замены NA значений:"),
                         " каждое пропущенное значение заменяется средним значением для каждого столбца;", html.Br(),
                         html.B("Использовать интерполяцию:"),
                         " каждое пропущенное значение заменяется результатом линейной интерполяции для каждого столбца"
                         ],
                        target="help-imputn",
                        placement='bottom',
                        delay={'show': 0,
                               'hide': 50},
                        style={'font-size': '1.5rem'})
                ],
                    className="p-title"),
                dcc.RadioItems(id='imputation_variation',
                               options=dict(v1='  Убрать все записи с NA значениями',
                                            v2='  Использовать среднее для замены NA значений',
                                            v3='  Использовать интерполяцию'),
                               value='v1'),
                html.Div([
                    html.Button('Преобразовать пустые строки', id='submit-NA', n_clicks=0)
                ],
                    className="div_btn mt-3"),
            ],
                width=12,
                className="component-block"
            ),
        ],
            width=4,
            className="offset-1"
        ),
        dbc.Col(
            children=[
                html.H3("Таблица данных"),
                html.Div(
                    children=[build_table(df)],
                    id='output-data-upload',
                ),
                html.Div(
                    children=[
                        html.H6(["Количество записей:"], id="num_row")
                    ]
                ),
                html.Div(
                    children=[
                        html.H6(["Количество записей с NaN значениями:"], id="num_na")
                    ]
                )
            ],
            width=5,
            className="offset-1 component-block"),
        dbc.Col(
            [],
            width=1),
        dbc.Col(
            children=[
                html.H3("Вычисление медианы"),
                html.H5(["Выбор режима вычисления \xa0",
                         html.I(className="bi bi-info-circle",
                                id="help-median",
                                style={'font-size': '1.5rem'}),
                         dbc.Tooltip(
                             ["Описание каждого режима:", html.Br(),
                              html.B("Вычислить доверительный интервал для медианы:"),
                              " вычислить доверительный интервал медианы для одной выборки "
                              "(необходимо  выбрать 1 столбец с данными выборки);", html.Br(),
                              html.B("Независимые выборки:"),
                              " процедура эксперимента и полученные результаты измерения некоторого свойства у испытуемых"
                              "одной выборки не оказывают влияния на особенности протекания этого же эксперимента и на результаты "
                              "измерения этого же свойства у испытуемых (респондентов) другой выборки "
                              "(необходимо выбрать 2 столбца из таблицы, определяющих группы испытуемых);", html.Br(),
                              html.B("Использовать интерполяцию:"),
                              " процедура эксперимента и полученные результаты измерения некоторого свойства, "
                              "проведенные на одной выборке, оказывают влияние на другую "
                              "(необходимо выбрать 2 столбца из таблицы, определяющих результаты одной и той же группы испытуемых в разные промежутки времени)"
                              ],
                             target="help-median",
                             placement='top',
                             delay={'show': 0,
                                    'hide': 50},
                             style={'font-size': '1.5rem'})
                         ]),
                dcc.RadioItems(id='calc_variation',
                               options=dict(v1='  Вычислить доверительный интервал для медианы',
                                            v2='  Независимые выборки',
                                            v3='  Зависимые выборки'),
                               value='v1'),
                html.Div([
                    html.H5("Выбор данных для вычисления медианы"),
                    dcc.Dropdown([],
                                 id="select_column",
                                 multi=True,
                                 searchable=False,
                                 placeholder=""),
                    html.Div(id='body-error-median'),
                    html.Div([
                        html.Button('Запустить вычисление', id='submit-calc', n_clicks=0)
                    ],
                        className="div_btn mt-3"),
                    html.H5("Результат"),
                    html.Div(id='output-median', children=[])
                ]),
            ],
            width=6,
            className="offset-3 component-block",
            id="calc-block",
            style={'display': 'none'}),
        dbc.Col(
            children=[
                html.H3("Полученные графики",
                        style={'text-align': 'center'}),
                dbc.Row(
                    children=[
                        html.Div(
                            children=dcc.Graph(
                                id="graph-median1",
                                responsive=False,
                            ),
                            className="col-12 card-graph",
                        ),
                        html.Div([
                            html.Div(
                                children=dcc.Graph(
                                    id="graph-median2",
                                    responsive=False,
                                ),
                                className="col-12 card-graph",
                            ),
                            html.Div(
                                children=dcc.Graph(
                                    id="graph-diff",
                                    responsive=False,
                                ),
                                className="col-12 card-graph",
                            ),
                            html.Div(
                                children=dcc.Graph(
                                    id="graph-summ",
                                    responsive=False,
                                ),
                                className="col-12 card-graph",
                            )
                        ],
                            id='v2_graph'),
                    ]
                )
            ],
            width=8,
            className="offset-2 component-block",
            id="figure-block",
            style={'display': 'none'}),
    ]),
    className="container-fluid content-fluid"
)


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif ("xls" in filename) or ('xlsx' in filename):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return 'format_err'
    except Exception as e:
        print(e)
        return 'another_err'
    return build_table(df)


# -------Перепостроение таблицы (включая обработку пропущенных значений)-------
@app.callback([Output('output-data-upload', 'children'),
               Output('calc-block', 'style'),
               Output('body-error-upload', 'children')],
              Input('upload-data', 'contents'),
              Input('submit-NA', 'n_clicks'),
              State('upload-data', 'filename'),
              State('table_data', 'data'),
              State('table_data', 'columns'),
              State('imputation_variation', 'value'))
def update_output(list_of_contents, n_clicks, list_of_names, data, columns, variation):
    ctx_id = dash.callback_context.triggered_id
    err = ""
    style = {'display': 'none'}
    if ctx_id == "upload-data":
        if list_of_contents is not None:
            if len(list_of_contents) > 1:
                return dash.no_update, style, out_error("Было прикреплено больше одного файла")
            children = [
                parse_contents(c, n) for c, n in
                zip(list_of_contents, list_of_names)]
            style = {'display': 'block'}
    elif ctx_id == "submit-NA":
        children = [build_table(remove_NA.execute(data, columns, variation))]
        style = {'display': 'block'}
    elif ctx_id is None:
        children = [build_table(df)]
    if isinstance(children[0], str) and (children[0] == 'format_err'):
        return dash.no_update, dash.no_update, out_error("Неверный формат файла")
    if isinstance(children[0], str) and (children[0] == 'another_err'):
        return dash.no_update, dash.no_update, out_error("Неизвестная ошибка. Обратитесь к разработчику")
    return children, style, ""


# -------Обновление списка колонок--------
@app.callback([Output('select_column', 'options'),
               Output('num_row', 'children'),
               Output('num_na', 'children')],
              Input('table_data', 'columns'),
              State('table_data', 'data'))
def update_output(columns, data):
    columns = list(pd.DataFrame.from_dict(columns)['name'])
    df = pd.DataFrame.from_dict(data)
    nas = df.isna().sum()
    return columns, f"Количество записей: {df.shape[0]}", f"Количество записей с NaN значениями: {nas.max()}"



# -------вычисление медианы-------
@app.callback([Output('output-median', 'children'),
               Output('figure-block', 'style'),
               Output('graph-median1', 'figure'),
               Output('graph-median2', 'figure'),
               Output('graph-diff', 'figure'),
               Output('graph-summ', 'figure'),
               Output('v2_graph', 'style'),
               Output('body-error-median', 'children')],
              Input('submit-calc', 'n_clicks'),
              State('table_data', 'data'),
              State('table_data', 'columns'),
              State('calc_variation', 'value'),
              State('select_column', 'value'))
def update_output(n_clicks, data, columns, variation, slt_columns):
    df = pd.DataFrame(data, columns=[c['name'] for c in columns])
    style_out = {'display': 'none'}
    style_v2_out = {'display': 'none'}
    if variation == 'v1':
        if slt_columns is None and n_clicks > 0:
            return dash.no_update, style_out, dash.no_update, dash.no_update, \
                   dash.no_update, dash.no_update, style_v2_out, out_error("Не выбран столбец")
        if df.dtypes[slt_columns] not in [np.int64, np.float64]:
            return dash.no_update, style_out, dash.no_update, dash.no_update, \
                   dash.no_update, dash.no_update, style_v2_out, out_error("Неверный тип данных в столбце")
        dict_m1 = calc_moda.find_moda(df, slt_columns, None, variation)
        result = build_result(dict_m1, None, None)
        style_out = {'display': 'block'}
        figure_m1 = graphs.to_build_distr(dict_m1, 'v1')
        figure_m2 = graphs.return_nan_figure()
        figure_diff = graphs.return_nan_figure()
        figure_summ = graphs.return_nan_figure()
    elif variation == 'v2' or variation == 'v3':
        if (len(slt_columns) != 2 or slt_columns is None) and n_clicks > 0:
            return dash.no_update, style_out, dash.no_update, dash.no_update, \
                   dash.no_update, dash.no_update, style_v2_out, out_error("Количество столбцов не равно 2")
        for col in slt_columns:
            if df.dtypes[col] not in [np.int64, np.float64]:
                return dash.no_update, style_out, dash.no_update, dash.no_update, \
                       dash.no_update, dash.no_update, style_v2_out, out_error(
                    f"Неверный тип данных в столбце \"{col}\"")
        dict_m1 = calc_moda.find_moda(df, slt_columns[0], None, 'v1')
        dict_m2 = calc_moda.find_moda(df, slt_columns[1], None, 'v1')
        dict_diff = calc_moda.find_moda(df, slt_columns[0], slt_columns[1], variation)
        result = build_result(dict_m1, dict_m2, dict_diff)
        style_out = {'display': 'block'}
        style_v2_out = {'display': 'block'}
        figure_m1 = graphs.to_build_distr(dict_m1, 'v1')
        figure_m2 = graphs.to_build_distr(dict_m2, 'v1')
        figure_diff = graphs.to_build_distr(dict_diff, 'v2')
        figure_summ = graphs.to_build_intervals([dict_diff, dict_m1, dict_m2])
    return result, style_out, figure_m1, figure_m2, figure_diff, figure_summ, style_v2_out, ""


# -------изменение настроек вычисления-------
@app.callback([Output('select_column', 'placeholder'),
               Output('select_column', 'multi')],
              Input('calc_variation', 'value'))
def update_output(variation):
    dict_result = dict.fromkeys(['ph', 'multi'])
    dict_result['multi'] = True
    if variation == 'v1':
        dict_result['ph'] = "Выберите 1 колонку"
        dict_result['multi'] = False
    elif variation == 'v2':
        dict_result['ph'] = "Выберите 2 колонки"
    elif variation == 'v3':
        dict_result['ph'] = "Выберите 2 колонки"
    return dict_result['ph'], dict_result['multi']


if __name__ == '__main__':
    app.run_server(debug=False)
