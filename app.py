'''
 # @ Create Time: 2024-05-30 12:06:01.442809
'''
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, State
import plotly.graph_objs as go
import numpy as np
from collections import deque
import dash_daq as daq
import datetime
import time
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title = "Experiment Control Panel")

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server





# Web Based UI for Experiment Sequence Control 
# Driver and Wrappers for Thorlabs PPC102 Piezo Motor, LabJack T7
# Babak Behjati 06.2024 


#___________

# Initialize the Dash app



# Data deque for live updates
data_x = deque(maxlen=1000)
data_y1 = deque(maxlen=1000)
data_y2 = deque(maxlen=1000)

# Initial data
data_x.extend(np.linspace(0, 10, 100))
data_y1.extend(np.sin(data_x))
data_y2.extend(np.cos(data_x))

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Experiment Control Pannel", className='text-center mb-4'), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='live-plot-1', animate=True), width=4),
        dbc.Col(dcc.Graph(id='live-plot-2', animate=True), width=4),
        dbc.Col(dcc.Graph(id='live-plot-3', animate=True), width=4)
        
    ]),
    #dcc.RadioItems(['New York City', 'Montreal','San Francisco'], 'Montreal'),
    dcc.Dropdown(['No ND Filter (OD = 0) ', 'OD = 1', 'OD = 2', 'OD = 3' , 'OD = 4', 'OD = 5' , 'OD = 6'], 'Filter Wheel Control', placeholder = 'Choose ND Filter' , id='demo-dropdown'), 
    
    dbc.Row([
        dbc.Col(dbc.Textarea(id='console', readOnly = 'True'
                             , placeholder= f'- Experiment Control Program \n Time : {datetime.datetime.now()}',  size='lg', style={'width' : '1295px' ,  'height': '300px'}), width=100 )
    ]),  dbc.Progress(label="Grid Sweep Sequence : 25%", value=25),
    dbc.Row([
        dbc.Col([dbc.Input(id=f'input-1',  placeholder=f'Enter Voltage for Channel 1 (Open Loop) ', type='text') ,
                 dbc.Input(id=f'input-2',  placeholder=f'Enter Voltage for Channel 2 (Open Loop)', type='text') ,
                 dbc.Input(id=f'input-3',  placeholder=f'Enter Position for Channel 1 (Closed Loop)', type='text') ,
                 dbc.Input(id=f'input-4',  placeholder=f'Enter Position for Channel 2 (Closed Loop)', type='text') ,
                 dbc.Input(id=f'input-6',  placeholder=f'Voltage Grid Sweep Step Size (In Volts) ', type='text') ,
                 dbc.Input(id=f'input-7',  placeholder=f'Voltage Inspection Range', type='text') ,
                 dbc.Input(id=f'input-8',  placeholder=f'Postion Grid Scan Step Size (In mrad)', type='text') ,
                 dbc.Input(id=f'input-9',  placeholder=f'Position Inspection Range', type='text') ,
                 dbc.Input(id=f'input-10', placeholder=f'Spectrometer Trigger ', type='text') ,
                 dbc.Input(id=f'input-11', placeholder=f'Input ', type='text') ,], width=6),
                 
        
        dbc.Col([dbc.Button(f'SM Update Position', id=f'button-1', outline=True , size='lg', color='success', className='mr-1'),
                 dbc.Button(f'SM Update Voltage', id=f'button-2', outline=True , size='lg', color='success', className='mr-1'),
                 dbc.Button(f'SM Home', id=f'button-3', outline=True , size='lg', color='info', className='mr-1'),
                 dbc.Button(f'SM Set Voltage CH1', id=f'button-4', outline=True, color='primary', size='lg', className='d-grid gap-2'),
                 dbc.Button(f'SM Set Voltage CH2', id=f'button-5', outline=True, color='primary', size='lg', className='d-grid gap-2'),
                 dbc.Button(f'SM Set Position CH1', id=f'button-6', outline=True, color='secondary', size='lg', className='d-grid gap-2'),
                 dbc.Button(f'SM Set Position CH2', id=f'button-7', outline=True, color='secondary', size='lg', className='mr-1'),
                 dbc.Button(f'Voltage Grid Sweep (Open Loop)', id=f'button-8', outline=True, color='danger', size='lg', className='d-grid gap-2'),
                 dbc.Button(f'Position Grid Scan (Closed Loop)', id=f'button-9', outline=True, color='dark', size='lg', className='d-grid gap-2'),
                 dbc.Button(f'Manual TTL to Spectrometer', id=f'button-10', outline=True, color='dark', size='lg', className='d-grid gap-2'),
                 dbc.Button(f'Initialize Measurement Sequence', id=f'button-11', outline=True, color='dark', size='lg', className='d-grid gap-2'),
                 dbc.Button(f'Start APD TTL Count', id=f'button-12', outline=True, color='dark', size='lg', className='d-grid gap-2'),
                 dbc.Button(f'SM OFF', id=f'button-13', outline=True, color='dark', size='lg', className='d-grid gap-2'),
                 dbc.Button(f'LabJack OFF', id=f'button-14', outline=True, color='dark', size='lg', className='d-grid gap-2'),
                 dbc.Button(f'Clear Console', id=f'button-15', outline=True, color='dark', size='lg', className='d-grid gap-2'),], width=6)
    ]),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0) 
])

# Callback to update plots
@app.callback(
    [Output('live-plot-1', 'figure'),
     Output('live-plot-2', 'figure'),
     Output('live-plot-3', 'figure')],
    [Input('interval-component', 'n_intervals')]
)



def update_live_plots(n):
    # Update data
    global data_x, data_y1, data_y2
    new_x = data_x[-1] + 0.1
    data_x.append(new_x)
    data_y1.append(np.sin(new_x))
    data_y2.append(np.cos(new_x))

    # Create plotly figures
    fig1 = go.Figure(data=[go.Scatter(x=list(data_x), y=list(data_y1), mode='lines', name='Sine Wave')])
    fig1.update_layout(title='Live APD TTL Counter: ')

    fig2 = go.Figure(data=[go.Scatter(x=list(data_x), y=list(data_y2), mode='lines' , marker = {'color' : 'red'}, name='Cosine Wave')])
    fig2.update_layout(title='Wave meter :  ')
    
    fig3 = go.Figure(data=[go.Scatter(x=list(data_x), y=list(data_y2), mode='lines', marker = {'color' : 'violet'}, name='Cosine Wave')])
    fig3.update_layout(title='Triggers to Spectrometer Demo :')

    return fig1, fig2, fig3

# Callback to update console and handle button clicks

@app.callback(
    Output('console', 'value'),
    [Input(f'button-1', 'n_clicks') , Input(f'button-2', 'n_clicks') , Input(f'button-3', 'n_clicks'),
     Input(f'button-4', 'n_clicks'), Input(f'button-5', 'n_clicks'), Input(f'button-6', 'n_clicks'),
     Input(f'button-7', 'n_clicks'), Input(f'button-8', 'n_clicks'), Input(f'button-9', 'n_clicks'),
     Input(f'button-10', 'n_clicks'), Input(f'button-11', 'n_clicks'), Input(f'button-12', 'n_clicks'),
     Input(f'button-13', 'n_clicks'), Input(f'button-14', 'n_clicks'), Input(f'button-15', 'n_clicks'),],
    [State('console', 'value')])


def update_console(*args):
    
    ctx = dash.callback_context
    
#_______SM Update Position :
    
    
    if  ctx.triggered_id == 'button-1':
        
         
        #sm_reconnect()
        #get_position()
        #activate_close_loop()
        #print(type(pos_ch1))  # type is System.Decimal and can not be converted into float        
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f'Channel 1 at {1} mrad\n' 
        time.sleep(.3)
        new_console_value = new_console_value + f'Channel 2 at {1} mrad\n' + f'\n'
        #new_console_value = console_value + f'just slept for 3 secs\n'
        return new_console_value

#_______SM Update Voltage:
  
    if  ctx.triggered_id == 'button-2':
        
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f'Steering Mirror Voltage Channel 1 and 2  \n'
        return new_console_value


    #     activate_open_loop()
    #     V_ch1 = channel_1.GetOutputVoltage()
    #     #print(type(pos_ch1))  # type is System.Decimal and can not be converted into float
    #     V_ch2 = channel_2.GetOutputVoltage()
    #     console_value = args[-1] if args[-1] else ""
    #     new_console_value = console_value + f'Channel 1 at {V_ch1} mrad\n' 
    #     time.sleep(.3)
    #     new_console_value = new_console_value + f'Channel 2 at {V_ch2} mrad\n' + f'\n'
    #     #new_console_value = console_value + f'just slept for 3 secs\n'
    #     sm_disconnect()
    #     return new_console_value
    
#______SM Home:
    
    if  ctx.triggered_id == 'button-3':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f'Steering Mirror Home Sequence Initiated \n'
        return new_console_value


#______SM Set Voltage CH1: 
    
    if  ctx.triggered_id == 'button-4':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f'Set Channel 2 Voltage to \n'
        return new_console_value

#______SM Set Voltage CH2: 
   
    if  ctx.triggered_id == 'button-5':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f'Set Channel 2 Voltage to \n'
        return new_console_value

#______SM Set Position CH1:

    if  ctx.triggered_id == 'button-6':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f'Voltage Grid Sweep\n'
        return new_console_value

#______SM Set Position CH2:


    if  ctx.triggered_id == 'button-7':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f'Position Grid Scan initialized \n'
        return new_console_value

#______Voltage Grid Sweep (Open Loop):
 

    if  ctx.triggered_id == 'button-8':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f'Initialize Measurement Sequence \n'
        return new_console_value


#______Position Grid Scan (Closed Loop):

    
    if  ctx.triggered_id == 'button-9':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f' Position Grid Scan (Closed Loop) \n'
        return new_console_value


#______Manual TTL to Spectrometer:

    if  ctx.triggered_id == 'button-10':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f'you just pressed button 2 \n'
        return new_console_value

#______LabJack OFF: 

    if  ctx.triggered_id == 'button-11':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = console_value + f'you just pressed button 2 \n'
        return new_console_value

#______Clear Console: 
   
    if  ctx.triggered_id == 'button-12':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = f'- Experiment Control Program \n Time : {datetime.datetime.now()}'
        return new_console_value
    
#______SM OFF: 
   
    if  ctx.triggered_id == 'button-13':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = f'- Experiment Control Program \n Time : {datetime.datetime.now()}'
        return new_console_value

#______LabJack OFF: 
   
    if  ctx.triggered_id == 'button-14':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = f'- Experiment Control Program \n Time : {datetime.datetime.now()}'
        return new_console_value

#______Clear Console: 
   
    if  ctx.triggered_id == 'button-15':
    
        console_value = args[-1] if args[-1] else ""
        new_console_value = f'- Experiment Control Program \n Time : {datetime.datetime.now()}'
        return new_console_value
    

#_____Functions_____________________________________________________





if __name__ == '__main__':
    app.run_server(debug=True)

