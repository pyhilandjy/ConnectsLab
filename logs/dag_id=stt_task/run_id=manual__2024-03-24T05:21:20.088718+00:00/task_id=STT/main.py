import dash
import dash_core_components as dcc
import dash_html_components as html
import pymysql
import pandas as pd

# MySQL 연결 정보
db_user = 'jun'
db_password = '1234qwer'
db_host = 'localhost'
db_port = 3306
db_name = 'STT'

app = dash.Dash(__name__)

@app.callback(
    Output("main-container", "children"),
    Input("dropdown", "value"),
)
def update_page(value):
    # 데이터베이스 연결
    con = pymysql.connect(user=db_user,
                          passwd=db_password,
                          host=db_host,
                          port=db_port,
                          db=db_name,
                          charset='utf8')

    # SQL 쿼리 실행 및 결과 데이터프레임으로 변환
    df = pd.read_sql(sql_query, con)

    # 데이터베이스 연결 닫기
    con.close()

    # 선택된 ID에 대한 텍스트 가져오기
    text = df.loc[df["id"] == value, "text"].iloc[0]

    return html.Div([
        html.H1("STT 대시보드"),
        dcc.Dropdown(
            id="dropdown",
            options=[{"label": row[1], "value": row[0]} for row in df.itertuples()],
            value=df.iloc[0][0],
        ),
        html.Div(id="text-output", children=text),
    ])

app.layout = html.Div(id="main-container")

if __name__ == "__main__":
    app.run_server(debug=True)
