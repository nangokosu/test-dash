import base64
import datetime
import io
import dash
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import dash_bootstrap_components as dbc
#import datetime as datetime
import plotly.express as px
from datetime import date
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

freq_retweets=pd.read_pickle("https://storage.googleapis.com/data_hoya/retweets_11.pkl")
user_list=pd.read_pickle('https://storage.googleapis.com/data_hoya/all_users.pkl')[['user_id','user_active_status','user_community']]
user_list.user_community=user_list.user_community.fillna('Others')
url_data=pd.read_csv('https://raw.githubusercontent.com/sTechLab/VoterFraud2020/main/data/urls.csv')
url_data=url_data.query('domain!="youtube.com"')
freq_retweets
tab1_content=html.Div(id="test_2")
tab2_content=html.Div(id="test_3")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
block1=html.Div([dcc.DatePickerRange(
        id="my_date_picker1",
        min_date_allowed=date(2020,11,1),
        max_date_allowed=date(2020,11,8),
        start_date=date(2020,11,1),
        end_date=date(2020,11,8),
        reopen_calendar_on_clear=True
    ),
    html.Div(id="bar2",children=[
        html.Div(id="test",children=[
            dcc.Graph(id="image")
        ]),

    ]),
    dbc.Tabs(
        [dbc.Tab(tab1_content,label="Velocity"),
        dbc.Tab(tab2_content,label="User status")],id="tabs",
    )]
)

block2=html.Div([
    html.H4("Choose your filter"),
    dcc.Dropdown(id='dropdown',
        options=[
            {'label': 'Total tweet count', 'value': 'tweet_count'},
            {'label': 'Total retweet count', 'value': 'retweet_count'},
            {'label': 'Total quote count', 'value': 'quote_count'}
        ],
        value='tweet_count'),
    html.Div(id="bar",children=[
        dcc.Graph("image_2"),
        html.Br(),
        html.Div(
        [html.H6(id="h6")]),
        dcc.Graph("image_3")
        ]),
    html.Br(),
    dbc.Tabs([
        dbc.Tab(id="comms_1",label="Community 1"),
        dbc.Tab(id="comms_2",label="Community 2"),
        dbc.Tab(id="comms_3",label='Community 3'),
        dbc.Tab(id="comms_4",label='Community 4'),
        dbc.Tab(id="comms_suspend",label='Suspended users'),
    ],id="tabs_2")
    ])
    


app.layout=dbc.Container(children=[
    block1,
    html.Br(),
    block2
])


@app.callback(Output("image","figure"),
[Input("my_date_picker1","start_date"),Input("my_date_picker1","end_date")])
def create_plot(start_date,end_date):
    start_date_object = pd.to_datetime(start_date)
    end_date_object = pd.to_datetime(end_date)
    condition1=freq_retweets.Date>=start_date_object
    condition2=freq_retweets.Date<=end_date_object
    freq_retweets_mini=freq_retweets[condition1&condition2]
    count=freq_retweets_mini.retweeted_id.value_counts()[:50]
    #thresh=count.quantile([0.50]).values[0]
    #count=count[count>=thresh]
    # Create the graph
    bar=go.Bar(x=[f"T_{element}" for element in count.index],y=list(count))
    layout=go.Layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig=go.Figure(data=bar,layout=layout)
    fig.update_traces(texttemplate='%{y:,}', textposition='outside',hovertemplate='Total number of retweets: %{y:,}'+"<extra></extra>")
    fig.update_layout(xaxis=dict(title='Top 50 tweets',showticklabels=False),
    yaxis=dict(title='Number of total retweets in the period'))
    fig.update_yaxes(tickformat=",d")
    return fig
    #return dcc.Graph(figure={
        #'data':[{'x':[f"T_{element}" for element in count.index],'y':list(count),'type':'bar'}]
    #})
    #return thresh

@app.callback(Output("test_2","children"),
[Input('image','clickData')],
[State("my_date_picker1","start_date"),State("my_date_picker1","end_date")])
def create_velocity(hoverData,start_date,end_date):
    if hoverData is None:
        return "Select a column above to continue"
    else:
        #return json.dumps(hoverData,indent=1)
        tweet_id=hoverData['points'][0]['x']
        start_date_object = pd.to_datetime(start_date)
        end_date_object = pd.to_datetime(end_date)
        condition1=freq_retweets.Date>=start_date_object
        condition2=freq_retweets.Date<=end_date_object
        condition3=freq_retweets.retweeted_id==int(tweet_id[2:])
        freq_retweets_mini=freq_retweets[condition1&condition2&condition3]
        freq_retweets_mini.Date=pd.to_datetime(freq_retweets_mini['Date']).dt.date
        freq_retweets_mini=freq_retweets_mini.merge(user_list,how="left")
        group_by=freq_retweets_mini.groupby(["Date","user_community"],as_index=False).count()
        scatter=[go.Scatter(x=group_by[group_by.user_community==element]["Date"],y=group_by[group_by.user_community==element]["retweeted_id"].cumsum(),mode='markers+lines',name=f"Community - {str(element)}") for element in group_by.user_community.unique() if group_by[group_by.user_community==element].shape[0]>0]
        layout=go.Layout(title='Retweet velocity',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(
        autorange=True),hovermode='x unified')
        fig=go.Figure(data=scatter,layout=layout)
        fig.update_xaxes(dtick=24*60*60*1000)
        fig.update_yaxes(tickformat=",d",title="Cumulative number of retweets")
        return dcc.Graph(figure=fig)

@app.callback(Output("test_3","children"),
[Input('image','clickData')],
[State("my_date_picker1","start_date"),State("my_date_picker1","end_date")])
def create_user(hoverData,start_date,end_date):
    if hoverData is None:
        return "Select a column above to continue"
    else:
        tweet_id=hoverData['points'][0]['x']
        start_date_object = pd.to_datetime(start_date)
        end_date_object = pd.to_datetime(end_date)
        condition1=freq_retweets.Date>=start_date_object
        condition2=freq_retweets.Date<=end_date_object
        condition3=freq_retweets.retweeted_id==int(tweet_id[2:])
        freq_retweets_mini=freq_retweets[condition1&condition2&condition3]
        freq_retweets_mini=freq_retweets_mini.merge(user_list,how="left")
        group_by=freq_retweets_mini.groupby(['user_community','user_active_status'],as_index=False).count()
        bar=[go.Bar(x=group_by[group_by.user_community==element]["user_active_status"],y=group_by[group_by.user_community==element]["retweeted_id"],name=f"Community - {str(element)}",hovertemplate="%{x}: %{y:,}"+"<extra></extra>") for element in group_by.user_community.unique() if group_by[group_by.user_community==element].shape[0]>0]
        layout=go.Layout(title='Status of users who retweeted as of Dec 2020',plot_bgcolor='rgba(0,0,0,0)',barmode="group")
        fig=go.Figure(data=bar,layout=layout)
        fig.update_yaxes(tickformat=",d")
        return dcc.Graph(figure=fig)

@app.callback(Output("image_2","figure"),
[Input('dropdown','value')])
def create_graph(value):
    if value != "tweet_count":
        value=f'{value}_metadata'
    new_data=url_data[["url",value]]
    new_data=new_data.sort_values(by=[value],axis=0,ascending=False).iloc[:50,:]
    bar=go.Bar(x=new_data['url'],y=new_data[value],hovertemplate='%{y:,}'+"<extra></extra>")
    layout=go.Layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig=go.Figure(data=[bar],layout=layout)
    fig.update_traces(texttemplate='%{y:,}', textposition='outside')
    fig.update_layout(xaxis=dict(title='Top 50 urls',showticklabels=False))
    fig.update_yaxes(tickformat=",d")
    return fig


@app.callback(Output("h6","children"),
[Input('image_2','hoverData')])
def create_link(hoverData):
    if hoverData is None:
        return [html.P('Link:',style={'display':'inline-block'})]
    else:
        url=hoverData['points'][0]['x']
        html_a=html.A(href=url,children=f' {url}',style={'display':'inline-block'})
        return [html.P('Link: ',style={'display':'inline-block'}),html_a]


@app.callback(Output("image_3","figure"),
[Input('dropdown','value')])
def create_graph_2(value):
    if value != "tweet_count":
        value=f'{value}_metadata'
    new_data=url_data.groupby(["domain"],as_index=False)[value].sum()
    new_data=new_data.sort_values(by=[value],axis=0,ascending=False).iloc[:20,:]
    bar=go.Bar(x=new_data['domain'],y=new_data[value])
    layout=go.Layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig=go.Figure(data=[bar],layout=layout)
    fig.update_traces(texttemplate='%{y:,}', textposition='outside',hovertemplate='%{x}'+"<extra></extra>")
    fig.update_layout(xaxis=dict(title='Top 20 domains',showticklabels=False))
    fig.update_yaxes(tickformat=",d")
    return fig

@app.callback(Output("comms_1","children"),
[Input('dropdown','value')])
def create_wind_rose_1(value_drop):
    #list_of_tabs=[]
    #for element in ["community_1","community_2","community_3","community_4","suspended_users"]:
    value=f"{value_drop}_by_community_1"
    new_data1=url_data[["domain",value]]
    new_data1=new_data1.query(f"{value}>0")
    new_data1=new_data1.groupby(["domain"],as_index=False)[value].sum()
    new_data1=new_data1.sort_values(by=[value],axis=0,ascending=False).iloc[:10,:]
    bar=go.Bar(x=new_data1['domain'],y=new_data1[value],hovertemplate="%{y}"+"<extra></extra>")
    layout=go.Layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig=go.Figure(data=[bar],layout=layout)
    fig.update_traces(texttemplate='%{y:,}', textposition='outside')
    fig.update_layout(xaxis=dict(title='Top 10 domains'),height=500)
    fig.update_yaxes(tickformat=",d")
    graph=dcc.Graph(figure=fig)
        #list_of_tabs.append(dbc.Tab(graph,label=f"{value_drop}"))
    return html.Div(children=[html.Br(),graph])

@app.callback(Output("comms_2","children"),
[Input('dropdown','value')])
def create_wind_rose_2(value_drop):
    #list_of_tabs=[]
    #for element in ["community_1","community_2","community_3","community_4","suspended_users"]:
    value=f"{value_drop}_by_community_2"
    new_data2=url_data[["domain",value]]
    new_data2=new_data2.query(f"{value}>0")
    new_data2=new_data2.groupby(["domain"],as_index=False)[value].sum()
    new_data2=new_data2.sort_values(by=[value],axis=0,ascending=False).iloc[:10,:]
    bar=go.Bar(x=new_data2['domain'],y=new_data2[value],hovertemplate="%{y}"+"<extra></extra>")
    layout=go.Layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig=go.Figure(data=[bar],layout=layout)
    fig.update_traces(texttemplate='%{y:,}', textposition='outside')
    fig.update_layout(xaxis=dict(title='Top 10 domains'),height=500)
    fig.update_yaxes(tickformat=",d")
    graph=dcc.Graph(figure=fig)
    return html.Div(children=[html.Br(),graph])

@app.callback(Output("comms_3","children"),
[Input('dropdown','value')])
def create_wind_rose_3(value_drop):
    #list_of_tabs=[]
    #for element in ["community_1","community_2","community_3","community_4","suspended_users"]:
    value=f"{value_drop}_by_community_3"
    new_data3=url_data[["domain",value]]
    new_data3=new_data3.query(f"{value}>0")
    new_data3=new_data3.groupby(["domain"],as_index=False)[value].sum()
    new_data3=new_data3.sort_values(by=[value],axis=0,ascending=False).iloc[:10,:]
    bar=go.Bar(x=new_data3['domain'],y=new_data3[value],hovertemplate="%{y}"+"<extra></extra>")
    layout=go.Layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig=go.Figure(data=[bar],layout=layout)
    fig.update_traces(texttemplate='%{y:,}', textposition='outside')
    fig.update_layout(xaxis=dict(title='Top 10 domains'),height=500)
    fig.update_yaxes(tickformat=",d")
    graph=dcc.Graph(figure=fig)
    return html.Div(children=[html.Br(),graph])

@app.callback(Output("comms_4","children"),
[Input('dropdown','value')])
def create_wind_rose_4(value_drop):
    #list_of_tabs=[]
    #for element in ["community_1","community_2","community_3","community_4","suspended_users"]:
    value=f"{value_drop}_by_community_4"
    new_data4=url_data[["domain",value]]
    new_data4=new_data4.query(f"{value}>0")
    new_data4=new_data4.groupby(["domain"],as_index=False)[value].sum()
    new_data4=new_data4.sort_values(by=[value],axis=0,ascending=False).iloc[:10,:]
    bar=go.Bar(x=new_data4['domain'],y=new_data4[value],hovertemplate="%{y}"+"<extra></extra>")
    layout=go.Layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig=go.Figure(data=[bar],layout=layout)
    fig.update_traces(texttemplate='%{y:,}', textposition='outside')
    fig.update_layout(xaxis=dict(title='Top 10 domains'),height=500)
    fig.update_yaxes(tickformat=",d")
    graph=dcc.Graph(figure=fig)
    return html.Div(children=[html.Br(),graph])

@app.callback(Output("comms_suspend","children"),
[Input('dropdown','value')])
def create_wind_rose_suspend(value_drop):
    #list_of_tabs=[]
    #for element in ["community_1","community_2","community_3","community_4","suspended_users"]:
    value=f"{value_drop}_by_suspended_users"
    new_data=url_data[["domain",value]]
    new_data=new_data.query(f"{value}>0")
    new_data=new_data.groupby(["domain"],as_index=False)[value].sum()
    #new_data=new_data.sort_values(by=[value],axis=0,ascending=False).iloc[:6,:]
    new_data=new_data.sort_values(by=[value],axis=0,ascending=False).iloc[:10,:]
    bar=go.Bar(x=new_data['domain'],y=new_data[value],hovertemplate="%{y}"+"<extra></extra>")
    layout=go.Layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    fig=go.Figure(data=[bar],layout=layout)
    fig.update_traces(texttemplate='%{y:,}', textposition='outside')
    fig.update_layout(xaxis=dict(title='Top 10 domains'),height=500)
    fig.update_yaxes(tickformat=",d")
    graph=dcc.Graph(figure=fig)
    return html.Div(children=[html.Br(),graph])

if __name__ == "__main__":
    app.run_server(debug=True)