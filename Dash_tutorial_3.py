#Multiple input/output for interactivity
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output,State
import pandas as pd
import plotly.express as px

gapminder=pd.read_csv("C:/Users/nango/plotly_materials/Data/gapminderDataFiveYear.csv")

new_app=Dash(__name__)
server=app.server
new_app.layout=html.Div(id="div-1",children=[
    dcc.Dropdown(id="dropdown-1",options=[{"label":continent,"value":continent} for continent in gapminder["continent"].unique()],value="Asia"),
    dcc.Dropdown(id="dropdown-2",options=[{"label":str(year),"value":year} for year in gapminder["year"].unique()],value=2002),
    dcc.Graph(id="graph"),
    html.Div(id="div-2",children=[
        dcc.RangeSlider(id="range-slider",min=0,max=20,step=2,value=[0,20],marks=dict([(number,str(number)) for number in range(0,21,2)])), #the input here is a list
        html.H1(id="heading-1")]),
    html.Button(id="submit-button",n_clicks=0,children="Submit here",style={'fontSize':24})
])

@new_app.callback(Output("graph","figure"),[Input("submit-button","n_clicks")],[State("dropdown-1","value"),State("dropdown-2","value")])
def draw_graph(n_clicks,continent,year):
    df=gapminder.query("continent=='{}' & year=={}".format(continent,year))
    graph=px.scatter(df,x="lifeExp",y="gdpPercap",color="country")
    graph.update_layout(hovermode="x")
    return graph


#this is callback without state.
#@new_app.callback(Output("heading-1","children"),[Input("range-slider","value")])
#def print_prod(value_list):
    #return value_list[0]*value_list[1]

@new_app.callback(Output("heading-1","children"),[Input("submit-button","n_clicks")],[State("range-slider","value")])
def print_prod(n_clicks,value_list):
    #This is how we create a state with callback i.e everything will only update upon the click of the HTML button.
    # More broadly speaking, state can just be anything that IS NOT an input.
    return value_list[0]*value_list[1]

if __name__ == "__main__":
    new_app.run_server(debug=True)
