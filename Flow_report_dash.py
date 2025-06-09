import tkinter as tk
from tkinter import messagebox
import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.express as px
import webbrowser
from threading import Timer, Thread
import socket
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html


# Function to start the Dash app
def start_dash_app(latest_file):
    #read the excel file
    df = pd.read_excel(latest_file)
   

    # Get the unique list of clients from the DataFrame
    client_options = [{'label': 'Client', 'value': 'all'}] + [{'label': client, 'value': client} for client in df['Client Name'].unique()]

    #Get the unique list of Tickers from the DataFrame
    ticker_options = [{'label': 'Ticker', 'value': 'all'}] + [{'label': ticker, 'value': ticker} for ticker in df['Grouping'].unique()]

    #Get the unique list of dates from the DataFrame
    date_options = [{'label': 'Date', 'value': 'all'}] + [{'label': date, 'value': date} for date in df['Date Traded'].unique()]
   
    app = dash.Dash(__name__)

    # Layout of the app
    app.layout = html.Div([
         #Centering the logo using a flexbox (CSS)
        html.Div([
            html.Img(
                src='https://static.vecteezy.com/system/resources/previews/047/656/219/non_2x/abstract-logo-design-for-any-corporate-brand-business-company-vector.jpg',
                style={'height': '200px', 'width': '200px'}
            )
        ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin-bottom': '15px'}),
        #Header
        html.H1('Trading Data Flow Report', style={'color': 'rgb(0, 0, 0)'}),
        
        #Unique identifier for the dropdown component (used in callbacks to reference user selection)
        dcc.Dropdown(
            id='timeframe-dropdown', #Unique identifier for the dropdown component (used in callbacks to reference user selection)
    
            options=[
                {'label': 'Previous Day', 'value': 'day'}, # Options for filetring by previous day
                {'label': 'Previous Week', 'value': 'prev_week'},
                {'label': 'Previous Month', 'value': 'prev_month'},
                {'label': 'Week to Date', 'value': 'week'},
                {'label': 'Month to Date', 'value': 'month'},
                {'label': 'Year to Date', 'value': 'year'}
            ],
            value='day' # Unique identifier for the dropdown component (used in callbacks to reference user selection)
        ),
        dcc.Dropdown(
            id='buy-sell-dropdown',
            options=[
                {'label': 'Side', 'value': 'all'},
                {'label': 'Buy', 'value': 'Buy'},
                {'label': 'Sell', 'value': 'Sell'}
            ],
            value='all' # Defult selected value - 'all' displays both buy and sell iniataly
        ),
        dcc.Dropdown(
            id='venue-type-dropdown',
            options=[
                {'label': 'Venue type', 'value': 'all'},
                {'label': 'Lit', 'value': 'Lit'},
                {'label': 'Dark', 'value': 'Dark'}
            ],
            value='all'
        ),
        dcc.Dropdown(
            id='region-dropdown',
            options=[
                {'label': 'Region', 'value': 'all'},
                {'label': 'America', 'value': 'America'},
                {'label': 'Asia', 'value': 'Asia'},
                {'label': 'Europe', 'value': 'Europe'}
            ],
            value='all'
        ),
        dcc.Dropdown(
            id='client-dropdown',
            options=client_options,
            value='all',  # Default value set to 'all'
            placeholder="Select a client"
        ),
        dcc.Dropdown(
            id='ticker-dropdown',
            options=ticker_options,
            value='all',  # Default value set to 'all'
            placeholder="Select a ticker"
        ),
        # Dropdown for selecting multiple dates
        dcc.Dropdown(
            id='date-dropdown',
            options=date_options,
            value=[],  # Default value set to an empty list for multiple selections
            placeholder="Select one or more dates",
            multi=True  # Enable multiple selections
        ),


        # Graphs
        # Section for rendering visual graphs on the dashboard
        # Each Graph component will be populated dynamically through callbacks using its unique ID
        dcc.Graph(id='value-by-side'),
        dcc.Graph(id='value-by-sectors'),
        dcc.Graph(id='value-by-client'),
        dcc.Graph(id='value-by-date'),
        dcc.Graph(id='exc-fig'),
        dcc.Graph(id='line-fig'),
        dcc.Graph(id='qty-by-client'),
        dcc.Graph(id='traded-by-region'),
        dcc.Graph(id='region-fig'),
        dcc.Graph(id='traded-by-destination')   
    ])


    # Callbacks
    # Dash callback function to dynamically update multiple graphs on the dashboard based on user inputs
    @app.callback(
        [
            #Outputs: these are the graph components whose 'figure' property will be updated when any input changes
            Output('value-by-sectors', 'figure'),
            Output('value-by-side', 'figure'),
            Output('value-by-client', 'figure'),
            Output('value-by-date', 'figure'),
            Output('line-fig', 'figure'),
            Output('qty-by-client', 'figure'),
            Output('traded-by-region', 'figure'),
            Output('traded-by-destination', 'figure'),
            Output('region-fig', 'figure'),
            Output('exc-fig', 'figure')
        ],
        [
            # Inputs: these are the dropdown values that trigger the callback when changed by the user
            Input('timeframe-dropdown', 'value'),
            Input('buy-sell-dropdown', 'value'),
            Input('venue-type-dropdown', 'value'),
            Input('region-dropdown', 'value'),
            Input('client-dropdown', 'value'),
            Input('ticker-dropdown', 'value'),
            Input('date-dropdown', 'value')
        ]
    )
    # Function to update the graphs based on user inputs
    #Note: Dash does not call the function explicitly in the code. 
    #Instead, Dash uses decorators like @app.callback(...) to "register" the function 
    #and call it automatically when inputs change in the UI.
    def update_graphs(timeframe, buy_sell, venue_type, region, client, ticker, dates, df=df):
        today = pd.to_datetime('today').normalize() # Get the current date
        last_trading_date = df['Date Traded'].max() # Get the last trading date

        # Filter the dataframe(df) based on the selected timeframe from the dropdown
        
        if timeframe == 'day':
            # Filter rows where the trade date is equal to the most recent trading day
            filtered_df = df[df['Date Traded'] == last_trading_date]     
        elif timeframe == 'prev_week':
            # Filter rows where the trade date is within the last 7 days (excluding today)
            filtered_df = df[
                (df['Date Traded'] < today) & 
                (df['Date Traded'] >= (today - pd.Timedelta(days=7)))
            ]     
        elif timeframe == 'prev_month':
            # Calculate the first day of the current and previous months
            first_day_of_current_month = today.replace(day=1)
            first_day_of_previous_month = (
                first_day_of_current_month - pd.DateOffset(months=1)
                ).replace(day=1) 
            # Filter for trades that happened in the previous calendar month
            filtered_df = df[
                (df['Date Traded'] < first_day_of_current_month) & 
                (df['Date Traded'] >= first_day_of_previous_month)
            ]   
        elif timeframe == 'week':
            # Filter for Week-to-Date: from the start of the current week (Monday) to today
            filtered_df = df[df['Date Traded'] >= (today - pd.Timedelta(days=today.dayofweek))]
        elif timeframe == 'month':
            # Filter for Month-to-Date: from the first day of the current month to today
            filtered_df = df[df['Date Traded'] >= today.replace(day=1)] 
        elif timeframe == 'year':
            # Filter for Year-to-Date: from Jan 1st of the current year to today
            filtered_df = df[df['Date Traded'] >= today.replace(month=1, day=1)]


        # Apply additional filters based on user selections from the dropdowns. Skips filtering if 'all' is selected
        if buy_sell != 'all':
            filtered_df = filtered_df[filtered_df['Side'] == buy_sell]
        if venue_type != 'all':
            filtered_df = filtered_df[filtered_df['Execution Venue Type (dark/lit)'] == venue_type]
        if region != 'all':
            filtered_df = filtered_df[filtered_df['Region'] == region]
        if client != 'all':
            filtered_df = filtered_df[filtered_df['Client Name'] == client]
        if ticker != 'all':
            filtered_df = filtered_df[filtered_df['Grouping'] == ticker]
        if dates:
            filtered_df = filtered_df[filtered_df['Date Traded'].isin(dates)]
       
       
        # Function to format numbers
        def format_number(value):
            if value >= 1_000_000:
                return f'${value / 1_000_000:.1f}M'  # Format in millions
            elif value >= 1_000:
                return f'${value / 1_000:.0f}K'     # Format in thousands
            else:
                return f'${value}' #or str'{value}' # If number is less than 1,000, return the number as a string or as is.

        side_agg = filtered_df.groupby('Side')['Traded Value (US$)'].sum().reset_index()
        date_agg = filtered_df.groupby('Date Traded')['Traded Value (US$)'].sum().reset_index()
        order_by_cli_agg = filtered_df.groupby(['Date Traded', 'Client Name'])['# Orders'].sum().reset_index()
       
        # Traded value by 'SuperSector' by date
        sectors_agg = filtered_df.groupby(['Date Traded', 'Industry SuperSector'])['Traded Value (US$)'].sum().reset_index()
        value_by_sectors = go.Figure()
        for sector in sectors_agg['Industry SuperSector'].unique():
            sector_data = sectors_agg[sectors_agg['Industry SuperSector'] == sector]
            value_by_sectors.add_trace(go.Bar(
                x=sector_data['Date Traded'],
                y=sector_data['Traded Value (US$)'],
                name=sector
            ))
        value_by_sectors.update_layout(
            title='Traded Value by SuperSector',
            yaxis_title='Traded Value (US$)',
            barmode='stack',
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            args=["type", "bar"],
                            label="Bar Graph",
                            method="restyle"
                        ),
                        dict(
                            args=["type", "line"],
                            label="Line Chart",
                            method="restyle"
                        )
                    ],
                    direction="down",
                ),
            ]
        )
        # Traded value by side
        value_by_side = go.Figure() # Initialize a new Plotly Figure object to hold the visualization
        # Add a donut chart (Pie chart with a hole in the center) representing traded value by trade "Side" (Buy/Sell)
        value_by_side.add_trace(go.Pie(
            labels=side_agg['Side'],
            values=side_agg['Traded Value (US$)'],
            name='Traded Value by Side',
            hole=0.5
        ))
        # Configure the layout and interactivity of the chart
        value_by_side.update_layout(
            title='Traded Value by Side',
            # Dropdown menu that allows users to toggle between Pie and Bar chart
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            args=["type", "pie"],
                            label="Pie Chart",
                            method="restyle"
                        ),
                        dict(
                            args=["type", "bar"],
                            label="Bar Graph",
                            method="restyle"
                        )
                    ],
                    direction="down",
                ),
            ]
        )
        #Traded value by client
        total_traded_value = filtered_df['Traded Value (US$)'].sum()
        # Calculate the traded value by client as a percentage
        client_agg = filtered_df.groupby('Client Name')['Traded Value (US$)'].sum().reset_index()
        client_agg['Percentage'] = (client_agg['Traded Value (US$)'] / total_traded_value) * 100


        # Create the figure
        value_by_client = go.Figure()
        for client in client_agg['Client Name'].unique():
            client_data = client_agg[client_agg['Client Name'] == client]
            value_by_client.add_trace(go.Bar(
                x=client_data['Client Name'],
                y=client_data['Percentage'],
                name=client,
                marker_color='rgb(0, 128, 0)',
                text=client_data['Percentage'].round(2).astype(str) + '%',  # Display percentage as text
                textposition='auto'
            ))


        # Update layout
        value_by_client.update_layout(
            title='Traded Value by Client',
            yaxis_title='Percentage',
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            args=["type", "bar"],
                            label="Bar Graph",
                            method="restyle"
                        ),
                        dict(
                            args=["type", "scatter"],
                            label="Scatter Plot",
                            method="restyle"
                        )


                    ],
                    direction="down",
                ),
            ]
        )
       


        # Traded value by date
        value_by_date = go.Figure()
        value_by_date.add_trace(go.Bar(
            x=date_agg['Date Traded'],
            y=date_agg['Traded Value (US$)'],
            name='Traded Value by Date',
            marker_color='rgb(0, 128, 0)',
            text=[format_number(val) for val in date_agg['Traded Value (US$)']],  # Format each number
            textposition='auto'
        ))
   
        value_by_date.update_layout(
            title='Traded Value by Date',
            yaxis_title='Traded Value (US$)',
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            args=["type", "bar"],
                            label="Bar Graph",
                            method="restyle"
                        ),
                        dict(
                            args=["type", "line"],
                            label="Line Chart",
                            method="restyle"
                        )
                    ],
                    direction="down",
                )
            ]
        )


        #Traded value by 'Venue' by date
        venue_date_agg = filtered_df.groupby(['Date Traded', 'Execution Venue'])['Traded Value (US$)'].sum().reset_index()
        bar_fig = go.Figure()
        for venue in venue_date_agg['Execution Venue'].unique():
            venue_data = venue_date_agg[venue_date_agg['Execution Venue'] == venue]
            bar_fig.add_trace(go.Bar(
                x=venue_data['Date Traded'],
                y=venue_data['Traded Value (US$)'],
                name=venue
            ))
        bar_fig.update_layout(
            title='Traded Value by Venue by Date',
            yaxis_title='Traded Value (US$)',
            barmode='stack',
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            args=["type", "bar"],
                            label="Bar Graph",
                            method="restyle"
                        ),
                        dict(
                            args=["type", "line"],
                            label="Line Chart",
                            method="restyle"
                        )
                    ],
                    direction="down",
                ),
            ]
        )
        # Traded Qty by client
        oby_agg = filtered_df.groupby('Client Name')['Traded Qty'].sum().reset_index()
        order_by_client = go.Figure()
        for client in oby_agg['Client Name'].unique():
            client_data = oby_agg[oby_agg['Client Name'] == client]
            order_by_client.add_trace(go.Bar(
                x=client_data['Client Name'],
                y=client_data['Traded Qty'],
                name=client,
                marker_color='rgb(0, 128, 0)',
                text=client_data['Traded Qty'].astype(str),
                #round to the zero decimal place
                texttemplate='%{text:.0f}',
                textposition='auto'
            ))


        order_by_client.update_layout(
            title='Traded Qty by Client',
            yaxis_title='Traded Qty',
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            args=["type", "bar"],
                            label="Bar Graph",
                            method="restyle"
                        ),
                        dict(
                            args=["type", "scatter"],
                            label="Scatter Plot",
                            method="restyle"
                        )
                    ],
                    direction="down",
                ),
            ]
        )
       


        # Traded value by 'Region' by date
        region_date_agg = filtered_df.groupby(['Date Traded', 'Region'])['Traded Value (US$)'].sum().reset_index()
        region_fig = go.Figure()
        for region in region_date_agg['Region'].unique():
            region_data = region_date_agg[region_date_agg['Region'] == region]
            region_fig.add_trace(go.Bar(
                x=region_data['Date Traded'],
                y=region_data['Traded Value (US$)'],
                name=region
            ))
        region_fig.update_layout(
            title='Traded Value by Region by Date',
            yaxis_title='Traded Value (US$)',
            barmode='stack',
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            args=["type", "bar"],
                            label="Bar Chart",
                            method="restyle"
                        ),
                        dict(
                            args=["type", "line"],
                            label="Line Chart",
                            method="restyle"
                        )
                    ],
                    direction="down",
                ),
            ]
        )


        # Traded value by Destination Initial(Algo)
        total_traded_value = filtered_df['Traded Value (US$)'].sum()
        # Calculate the traded value by Destination Initial as a percentage
        destination_agg = filtered_df.groupby('Destination Initial')['Traded Value (US$)'].sum().reset_index()
        destination_agg['Percentage'] = (destination_agg['Traded Value (US$)'] / total_traded_value) * 100


        # Create the figure
        traded_by_destination = go.Figure()
        for destination in destination_agg['Destination Initial'].unique():
            destination_data = destination_agg[destination_agg['Destination Initial'] == destination]
            traded_by_destination.add_trace(go.Bar(
                x=destination_data['Destination Initial'],
                y=destination_data['Percentage'],
                name=destination,
                #marker_color='rgb(0, 128, 0)',
                text=destination_data['Percentage'].round(2).astype(str) + '%',  # Display percentage as text
                textposition='auto'
            ))


            # Update layout
        traded_by_destination.update_layout(
            title='Traded Value by Destination Initial',
            yaxis_title='Percentage',
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            args=["type", "bar"],
                            label="Bar Graph",
                            method="restyle"
                        ),
                        dict(
                            args=["type", "scatter"],
                            label="Scatter Plot",
                            method="restyle"
                        )
                    ],
                    direction="down",
                ),
            ]
        )


        # Group the data by 'Date Traded' and 'Region'
        region_date_agg = filtered_df.groupby(['Date Traded', 'Region'])['Traded Value (US$)'].sum().reset_index()
        # Create an animated scatter plot
        fig = px.scatter(
            region_date_agg,
            x='Region',
            y='Traded Value (US$)',
            animation_frame='Date Traded',
            animation_group='Region',
            size='Traded Value (US$)',
            color='Region',
            hover_name='Region',
            size_max=80,
            range_y=[0, region_date_agg['Traded Value (US$)'].max() + 500]
        )


        fig.update_layout(
            title='Traded Value by Region Over Time',
            xaxis_title='Region',
            yaxis_title='Traded Value (US$)',
        )

        # Excution Venue by Venue Type
        filtered_df = df


        # Function to get top 4 venues and sum the rest as "Others"
        def get_top_venues(dataframe, venue_type):
            # Filter data for the given venue type
            venue_data = dataframe[dataframe['Execution Venue Type (dark/lit)'] == venue_type]
           
            # Sum traded values for each venue
            venue_data = venue_data.groupby('Execution Venue', as_index=False)['Traded Value (US$)'].sum()


            # Sort venues by traded value in descending order
            venue_data = venue_data.sort_values(by='Traded Value (US$)', ascending=False)


            # Separate top 4 venues
            top_venues = venue_data.iloc[:4]


            # Sum the rest as "Others"
            others_value = venue_data.iloc[4:]['Traded Value (US$)'].sum()
            if others_value > 0:
                others = pd.DataFrame({
                    'Execution Venue': ['Others'],
                    'Traded Value (US$)': [others_value]
                })
                # Concatenate the top 4 venues with "Others"
                top_venues = pd.concat([top_venues, others], ignore_index=True)


            return top_venues


        # Get top venues for both 'Lit' and 'Dark' venue types
        lit_top_venues = get_top_venues(filtered_df, 'Lit')
        dark_top_venues = get_top_venues(filtered_df, 'Dark')


        # Create subplots: use 'domain' type for Pie subplot
        exc_fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])


        # Add pie chart for 'Lit' venues
        exc_fig.add_trace(go.Pie(labels=lit_top_venues['Execution Venue'], values=lit_top_venues['Traded Value (US$)'], name="Lit Venues"),
                    1, 1)


        # Add pie chart for 'Dark' venues
        exc_fig.add_trace(go.Pie(labels=dark_top_venues['Execution Venue'], values=dark_top_venues['Traded Value (US$)'], name="Dark Venues"),
                    1, 2)


        # Use `hole` to create a donut-like pie chart
        exc_fig.update_traces(hole=.5, hoverinfo="label+percent+name")


        exc_fig.update_layout(
            title_text="Lit VS Dark Venue Execution",
            # Add annotations in the center of the donut pies.
            annotations=[dict(text='Lit', x=0.20, y=0.5, font_size=20, showarrow=False),
                        dict(text='Dark', x=0.80, y=0.5, font_size=20, showarrow=False)]
        )
               

        # Update the layout of the figure
        return value_by_sectors, value_by_side, value_by_client, value_by_date, bar_fig, order_by_client, region_fig, traded_by_destination, fig, exc_fig



    # Find an available port dynamically on localhost
    port = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket object
    port.bind(("", 0)) # Bind the socket to an empty string (which means localhost) and port 0 and  the OS selects an available port automatically
    port = port.getsockname()[1] # Get the port number assigned by the OS

    #Automatically open the web browser to the app
    def open_browser():
        webbrowser.open(f"http://localhost:{port}") # Open the web browser to the Dash app URL

    Timer(1, open_browser).start()

    # Run the Dash app
    app.run_server(port=port)
 
#Function to handle login and report download
def login():
    print("Logging in...")

    if len(eUser.get()) == 0 or len(ePass.get()) == 0:
        messagebox.showerror("Error", "Enter User ID/Password")
        return

    # Hardcoded login credentials
    username = "user"
    password = "user123"

    if eUser.get() != username or ePass.get() != password:
        messagebox.showerror("Error", "Invalid User ID/Password")
        return

    print("Credentials accepted, proceeding...")

    # Path to the Excel file in Downloads
    downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    #target_file = os.path.join(downloads_folder, 'Copy of sample_post_trade_data_50000_rows.xlsx')
    target_file = os.path.join(downloads_folder, 'Copy of sample_post_trade_data_50000_rows_until_2025_03_31.xlsx')

    if os.path.exists(target_file):
        print("File found:", target_file)

        # Start Dash app in a separate thread
        def launch_and_exit():
            start_dash_app(target_file)
            # We do NOT destroy the tkinter root here

        dash_thread = Thread(target=launch_and_exit)
        dash_thread.start()

        # Instead of destroying immediately, just hide the window
        root.withdraw()
    else:
        messagebox.showerror("File Not Found", f"'Copy of sample_post_trade_data_50000_rows_until_2025_03_31' not found in Downloads folder.")



# Create the main window/User Interface for the application
root = tk.Tk()
root.title("Company Insight PostTrade")
root.minsize(400, 225)
root.maxsize(400, 225)
root.resizable(width=True, height=False)


# Title Frame
frame01 = tk.Frame(root, width=500, height=50, bg="#eb2d37")
labelFrame01 = tk.Label(frame01, text="Company Flow Report", font=("Bahnschrift Condensed", 24), bg= "#eb2d37", fg="white")
labelFrame01.place(x=0, y=0)
frame01.place(x=0, y=0)


# Main Frame
frame02 = tk.Frame(root, width=400, height=460, bg='#eb2d37')
frame02.place(x=0, y=50)
labelUser = tk.Label(frame02, text="Username:", font=("Bahnschrift Condensed", 14), bg= "#eb2d37", fg="white")
labelPass = tk.Label(frame02, text="Password:", font=("Bahnschrift Condensed", 14), bg= "#eb2d37", fg="white")
labelUser.place(x=0, y=0)
labelPass.place(x=0, y=30)
eUser = tk.Entry(frame02, width=41)
ePass = tk.Entry(frame02, width=41, show="*")  # the show hides the password
eUser.place(x=80, y=5)
ePass.place(x=80, y=35)


# Button Frame
frame03 = tk.Frame(root, width=325, height=320, bg= "#eb2d37")
frame03.place(x=5, y=120)


process_button = tk.Button(frame03, text="Log On & Download", font=("Bahnschrift Condensed", 12), width=50, command=login)
process_button.place(x=10, y=10)


# Run the Tkinter main loop
root.mainloop()