import base64
import io
import dash_bootstrap_components as dbc
import dash

import Calc_Class
import calc_median
import remove_NA
import graphs

from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
from dash.dash_table.Format import Format, Scheme, Trim

import pandas as pd
import numpy as np
from Calc_Class import *

dbc_css = ("https://codepen.io/chriddyp/pen/bWLwgP.css")
dbc_BTicons = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css"
dbc_AWicons = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css, dbc_AWicons, dbc_BTicons])
app.title = 'Доверительный интервал для медиан и их разностей: автоматизация расчета и визуализация'
# app._favicon = ("path_to_folder/your_icon.ico")

df = pd.DataFrame()
medianSystem = CalcMedianSystem()


def build_table(data):
    return html.Div([
        dash_table.DataTable(
            data=data.to_dict('records'),
            columns=[{'name': i, 'id': i, 'type': 'numeric',
                      'format': Format(precision=2, scheme=Scheme.fixed, trim=Trim.yes)} for i in data.columns],
            id='table_data'
        )
    ])


def out_error(text):
    return html.P([
        html.B(["Ошибка: "]),
        text
    ],
        style={'color': 'red'})


def build_result(result_clmn1, result_clmn2, result_diff, alpha):
    median1 = np.round(result_clmn1['median'], 2)
    low1 = np.round(result_clmn1['low'], 2)
    up1 = np.round(result_clmn1['up'], 2)
    if result_diff is not None:
        median2 = np.round(result_clmn2['median'], 2)
        low2 = np.round(result_clmn2['low'], 2)
        up2 = np.round(result_clmn2['up'], 2)
        return html.Div([
            html.H5("Результат"),
            html.P([html.B("Медиана №1 (столбец \"" + result_clmn1['column'] + "\"): "), str(median1)]),
            html.P([html.B("Нижняя граница: "), str(low1)]),
            html.P([html.B("Верхняя граница: "), str(up1)]),
            html.P([html.B("Представление: "), str(median1) + f" {alpha}% ДИ [" + str(low1) + ";" + str(up1) + "]"]),
            html.Br(),
            html.P([html.B("Медиана №2 (столбец \"" + result_clmn2['column'] + "\"): "), str(median2)]),
            html.P([html.B("Нижняя граница: "), str(low2)]),
            html.P([html.B("Верхняя граница: "), str(up2)]),
            html.P([html.B("Представление: "), str(median2) + f" {alpha}% ДИ [" + str(low2) + ";" + str(up2) + "]"]),
            html.Br(),
            html.P([html.B("Разница медиан: "), str(np.round(result_diff['median'], 2)) + f" {alpha}% ДИ [" +
                    str(np.round(result_diff['low'], 2)) + ";" + str(np.round(result_diff['up'], 2)) + "]"])
        ])
    else:
        return html.Div([
            html.H5("Результат"),
            html.P([html.B("Медиана №1 (столбец \"" + result_clmn1['column'] + "\"): "), str(median1)]),
            html.P([html.B("Нижняя граница: "), str(low1)]),
            html.P([html.B("Верхняя граница: "), str(up1)]),
            html.P([html.B("Представление: "), str(median1) + f" {alpha}% ДИ [" + str(low1) + ";" + str(up1) + "]"])
        ])


app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.A([
                        html.Img(
                            src="assets/img/logo.png",
                            height=100)
                    ],
                        href="https://health-family.ru/ru/",
                        className="logo-info"
                    )],
                    id="logo",
                    width=3),
                dbc.Col([
                    html.Span(["Федеральное государственное бюджетное научное учреждение"],
                              className="uppercase")
                ],
                    width=6),
                dbc.Col([],
                        width=3),
            ]),
            dbc.Row([
                html.Span([
                    html.P(["ДОВЕРИТЕЛЬНЫЙ ИНТЕРВАЛ ДЛЯ МЕДИАН И ИХ РАЗНОСТЕЙ:"]),
                    html.P(["АВТОМАТИЗАЦИЯ РАСЧЕТА И ВИЗУАЛИЗАЦИЯ"])
                ],
                    id="title",
                    className="uppercase")],
                align="center"
            )
        ],
            id="navbar",
            className="col-12"
        ),
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
                         html.Br(), ".XLSX, .XLS", html.Br(),
                         "Можно прикрепить только один файл размером не больше 2 МБ!"
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
                html.Div([
                    html.Button("Пример файла для загрузки",
                                id="btn_ex",
                                style={"width": "auto"}),
                    dcc.Download(id="download-example")],
                    style={"text-align": "center"}
                ),
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
                         html.B("Использовать медиану для замены NA значений:"),
                         " каждое пропущенное значение заменяется медианой для каждого столбца;", html.Br(),
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
                                            v3='  Использовать медиану для замены NA значений',
                                            v4='  Использовать интерполяцию'),
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
                              html.B("Вычисление доверительный интервал для медианы:"),
                              " вычислить доверительный интервал медианы для одной выборки "
                              "(необходимо  выбрать 1 столбец с данными выборки);", html.Br(),
                              html.B("Вычисление доверительного интервала разницы медиан для независимых выборок:"),
                              " процедура эксперимента и полученные результаты измерения некоторого свойства у испытуемых"
                              "одной выборки не оказывают влияния на особенности протекания этого же эксперимента и на результаты "
                              "измерения этого же свойства у испытуемых (респондентов) другой выборки "
                              "(необходимо выбрать 2 столбца из таблицы, определяющих группы испытуемых);", html.Br(),
                              html.B("Вычисление доверительного интервала разницы медиан для зависимых выборок:"),
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
                                            v2='  Вычислить доверительный интервал для независимых выборок',
                                            v3='  Вычислить доверительный интервал для зависимых выборок'),
                               value='v1'),
                html.H5("Уровень значимости"),
                dcc.RadioItems(id='alpha_variation',
                               options={
                                   '90': '\xa090%',
                                   '95': '\xa095%',
                                   '98': '\xa098%',
                                   '99': '\xa099%',
                                   '99,9': '\xa099.9%'},
                               value='90'),
                html.Div([
                    html.H5("Выбор данных для вычисления медианы"),
                    html.P(["Выберите переменную(-ые)"]),
                    dcc.Dropdown([],
                                 id="select_column",
                                 multi=True,
                                 searchable=False,
                                 placeholder=""),
                    html.P(["Выберите группирующую переменную"], id="title_dropdown_factor"),
                    dcc.Dropdown([],
                                     id="select_factor",
                                     multi=True,
                                     searchable=False,
                                     placeholder=""),
                    html.P(["Выберите идентификаторы групп"], id="title_factor_unique"),
                    dcc.Dropdown([],
                                     id="select_unique_factor",
                                     multi=True,
                                     searchable=False,
                                     placeholder="Выберите 2 значения"),
                    html.Div(id='body-error-median'),
                    html.Div([
                        html.Button('Запустить вычисление', id='submit-calc', n_clicks=0)
                    ],
                        className="div_btn mt-3"),
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
            style={'display': 'none'})],
        className="container-fluid content-fluid non_indent"),
    dbc.Row([
        dbc.Col([
            html.B("Контакты:")
        ],
            className="offset-1 col-3")
    ],
        className="container-fluid content-fluid non_indent",
        id="footer")
]
)


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if len(decoded) > 2097152:
        return 'size_err'
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            medianSystem.set_table(df)
        elif ("xls" in filename) or ('xlsx' in filename):
            df = pd.read_excel(io.BytesIO(decoded))
            medianSystem.set_table(df)
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
              [Input('upload-data', 'contents'),
               Input('submit-NA', 'n_clicks')],
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
        #cols = medianSystem.get_table().columns
        #value = cols[0]
        #children = [build_table(remove_NA.execute(data, columns, variation))]
        children = [build_table(medianSystem.remove_na(variation))]
        style = {'display': 'block'}
    elif ctx_id is None:
        children = [build_table(medianSystem.get_table())]
    if isinstance(children[0], str) and (children[0] == 'size_err'):
        return dash.no_update, dash.no_update, out_error("Размер файла больше 2Мбайт")
    if isinstance(children[0], str) and (children[0] == 'format_err'):
        return dash.no_update, dash.no_update, out_error("Неверный формат файла")
    if isinstance(children[0], str) and (children[0] == 'another_err'):
        return dash.no_update, dash.no_update, out_error("Неизвестная ошибка. Обратитесь к разработчику")
    return children, style, ""


# -------Обновление списка колонок--------
@app.callback([Output('select_column', 'options'),
               Output('select_factor', 'options'),
               Output('num_row', 'children'),
               Output('num_na', 'children')],
              Input('table_data', 'columns'),
              State('table_data', 'data'))
def update_output(columns, data):
    #columns = list(pd.DataFrame.from_dict(columns)['name'])
    columns = medianSystem.get_table().columns
    #df = pd.DataFrame.from_dict(data)
    df = medianSystem.get_table()
    nas = df.isna().sum()
    return columns, columns, f"Количество записей: {df.shape[0]}", f"Количество записей с NaN значениями: {nas.max()}"

#----------обновление уникальных значений----------
@app.callback(
    Output("select_unique_factor", "options"),
    Input("select_factor", "value"),
)
def update_output(column):
    df = medianSystem.get_table()
    unique_values = df[column].unique()
    return [{'label': i, 'value': i} for i in unique_values]



#-------вычисление медианы-------
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
              State('alpha_variation', 'value'),
              State('select_column', 'value'))
def update_output(n_clicks, data, columns, variation, alpha, slt_columns):
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
        dict_m1 = calc_median.find_moda(df, slt_columns, None, variation, alpha)
        result = build_result(dict_m1, None, None, alpha)
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
        dict_m1 = calc_median.find_moda(df, slt_columns[0], None, 'v1', alpha)
        dict_m2 = calc_median.find_moda(df, slt_columns[1], None, 'v1', alpha)
        dict_diff = calc_median.find_moda(df, slt_columns[0], slt_columns[1], variation, alpha)
        result = build_result(dict_m1, dict_m2, dict_diff, alpha)
        style_out = {'display': 'block'}
        style_v2_out = {'display': 'block'}
        figure_m1 = graphs.to_build_distr(dict_m1, 'v1')
        figure_m2 = graphs.to_build_distr(dict_m2, 'v1')
        figure_diff = graphs.to_build_distr(dict_diff, 'v2')
        figure_summ = graphs.to_build_intervals([dict_diff, dict_m1, dict_m2])
    return result, style_out, figure_m1, figure_m2, figure_diff, figure_summ, style_v2_out, ""


# -------изменение настроек вычисления-------
@app.callback([Output('select_column', 'placeholder'),
               Output('select_column', 'multi'),
               Output('select_factor', 'placeholder'),
               Output('select_factor', 'multi'),
               Output('select_factor', 'style'),
               Output('title_dropdown_factor', 'style'),
               Output('select_unique_factor', 'style'),
               Output('title_factor_unique', 'style')],
              Input('calc_variation', 'value'))
def update_output(variation):
    dict_props_columns, dict_props_factors = dict.fromkeys(['placeholder', 'multi']), dict.fromkeys(['placeholder', 'multi'])
    dict_props_columns['multi'], dict_props_factors['multi'] = False, False
    dict_props_columns['placeholder'],  dict_props_factors["placeholder"] = "Выберите 1 колонку", "Выберите 1 колонку"
    visibility_factors = 'none'
    if variation == 'v2':
        visibility_factors = 'block'
    elif variation == 'v3':
        dict_props_columns['placeholder'] = "Выберите 2 колонки"
        dict_props_columns['multi'] = True
    style = {'display': visibility_factors}
    return dict_props_columns['placeholder'], dict_props_columns['multi'], \
           dict_props_factors['placeholder'], dict_props_factors["multi"], style, style, \
           style, style


@app.callback(
    Output("download-example", "data"),
    Input("btn_ex", "n_clicks"),
    prevent_initial_call=True,
)
def update_output(n_clicks):
    return dcc.send_file(
        "example.xlsx"
    )


server = app.server
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=False)
