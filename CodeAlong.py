from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output,State
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
#import pandas_datareader.data as web
import yfinance as yf

options=[{"label":"Tesla","value":"TSLA"},{"label":"Microsoft","value":"MSFT"},{"label":"Disney","value":"DIS"}]
#dcc.Dropdown(id="stock-options",options=options,value="TSLA")


app = Dash()
app.layout = html.Div([html.H1("Stock Ticker Dashboard"),
#html.Div([html.H3("Enter a stock:"),
#dcc.Input(id="my_stock_pick",value="TSLA")],style={"display":"inline-block"}),
html.Div([html.H3("Choose your date:"),
dcc.DatePickerRange(id="time_pick",min_date_allowed=datetime(2015,1,1),
max_date_allowed=datetime.today(),start_date=datetime(2019,1,1),end_date=datetime.today())],style={"padding":"90px"}),
dcc.Graph(id="graphing"),
dcc.Dropdown(id="stock-options",options=options,value="TSLA",multi=True),
html.Button(id="submit-button",n_clicks=0,children="Submit here",style={"marginLeft":"30px"})])

@app.callback(Output("graphing","figure"),[Input("submit-button","n_clicks")],[State("stock-options","value"),State("time_pick","start_date"),State("time_pick","end_date")])
def draw_stock(n_clicks,tickers,start_date,end_date):
    #Note that Dash will consider both start_date and end_date as strings
    start_date=pd.to_datetime(start_date)
    end_date=pd.to_datetime(end_date)
    
    if isinstance(tickers,str):
        ticker=yf.Ticker(tickers)
        df=ticker.history(period="max")[start_date:end_date]
        df=df["Close"]
        #df=df.rename("{}".format(tickers))
        return px.line(df,x=df.index,y="Close")
    
    else:
        stock_list=[]
        for stock in tickers:
            ticker=yf.Ticker(stock)
            df=ticker.history(period="max")[start_date:end_date]
            df=df["Close"]
            df=df.rename("{}".format(stock))
            stock_list.append(df)
        stocks=pd.concat(stock_list,axis=1)
        stocks=stocks.reset_index().melt(id_vars="Date",var_name="Ticker",value_name="Closing_price")
        return px.line(x=stocks.Date,y=stocks.Closing_price,color=stocks.Ticker)

if __name__ == "__main__":
    app.run_server(debug=True)