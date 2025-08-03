import plotly.graph_objs as go
import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as pc
import pandas as pd

from data_handler.stock_data import StockDataHandler

class StockVisualizer:

    def __init__(self):
        self.data_handler = StockDataHandler()

    def plot_candles_stick_bar(_self,df, title="", currency=""):

        rows = 1
        row_heights = [7]
        for col_name in df.columns:
            if col_name in ['Volume', 'MACD', 'ATR', 'RSI']:
                rows += 1
                row_heights.append(3)

        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                            vertical_spacing=0.01,
                            subplot_titles=None,
                            row_heights=row_heights
                            )

        fig.update_xaxes(title_text="Date", row=rows, col=1)

        row = 1
        fig.add_trace(go.Candlestick(x=df.index,
                                    open=df['Open'],
                                    high=df['High'],
                                    low=df['Low'],
                                    close=df['Close'],
                                    name="OHVC",
                                    ),
                    row=1, col=1)

        for col_name in df.columns:

            if 'SMA' in col_name or 'EMA' in col_name:
                fig.add_trace(go.Scatter(x=df.index,
                                        y=df[col_name],
                                        mode='lines',
                                        line=dict(
                                            #color='black',
                                            width=2
                                        ),
                                        name=col_name),
                            row=1, col=1)

            elif 'Crossover' in col_name:

                first_period = col_name.split('_')[1].split('/')[0]

                for i, v in df[col_name].items():

                    if v == 1.0:  # Buy signal

                        fig.add_annotation(x=df.index[i], y=df[f'SMA_{first_period}'][i],
                                        text="Golden cross",
                                        showarrow=True,
                                        arrowhead=1,
                                        arrowsize=1,
                                        ay=60
                                        )

                    if v == -1.0:  # Sell signal

                        fig.add_annotation(x=df.index[i], y=df[f'SMA_{first_period}'][i],
                                        text="Death cross",
                                        showarrow=True,
                                        arrowhead=1,
                                        arrowsize=1,
                                        ay=-60
                                        )

            if col_name == 'Volume':
                row += 1

                volume_colors = ['green' if df['Close'].iloc[i] > df['Open'].iloc[i] else 'red' for i in range(len(df))]

                fig.add_trace(go.Bar(x=df.index,
                                    y=df[col_name],
                                    name=col_name,
                                    marker_color=volume_colors,
                                    hovertemplate=
                                    '%{x}<br>' +
                                    'Volume: %{y}<br>' +
                                    'ΔVolume: %{customdata[0]}<extra></extra>',
                                    customdata=df[["ΔVolume%"]].values
                                    ),
                            row=row, col=1)

                fig.update_yaxes(title_text="Volume", row=row, col=1)

            elif col_name == 'MACD':
                row += 1

                fig.add_trace(go.Scatter(x=df.index,
                                        y=df[col_name],
                                        name=col_name,
                                        ),
                            row=row, col=1)

                fig.update_yaxes(title_text="MACD", row=row, col=1)

                if 'Signal' in df.columns:
                    fig.add_trace(go.Scatter(x=df.index,
                                            y=df['Signal'],
                                            name='Signal',
                                            ),
                                row=row, col=1)

                if 'MACD_Hist' in df.columns:
                    MACD_colors = ['green' if df['MACD_Hist'][i] > 0 else 'red' for i in range(len(df))]

                    fig.add_trace(go.Bar(x=df.index,
                                        y=df['MACD_Hist'],
                                        name='MACD_Hist',
                                        marker_color=MACD_colors),
                                row=row, col=1)

            elif col_name == 'ATR':
                row += 1

                fig.add_trace(go.Scatter(x=df.index,
                                        y=df[col_name],
                                        name=col_name,
                                        ),
                            row=row, col=1)

                fig.update_yaxes(title_text="ATR", row=row, col=1)

            elif col_name == 'RSI':
                row += 1

                fig.add_trace(go.Scatter(x=df.index,
                                        y=df[col_name],
                                        name=col_name,
                                        ),
                            row=row, col=1)

                fig.update_yaxes(title_text="RSI", row=row, col=1)

                fig.add_hline(y=70, line_dash="dash", annotation_text='top', row=row, col=1)
                fig.add_hline(y=30, line_dash="dash", annotation_text='bottom', row=row, col=1)
                fig.add_hrect(y0=30, y1=70, fillcolor="blue", opacity=0.25, line_width=0, row=row, col=1)

        fig.update_layout(
            title=title,
            # xaxis_title='Date',
            yaxis_title=f'Price (in {currency})',
            # xaxis2_title='Date',
            # yaxis2_title='Volume',
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",  # Aligns the legend vertically to the top
                y=-0.15,  # Positions the legend below the subplots
                xanchor="center",  # Aligns the legend horizontally to the center
                x=0.5  # Centers the legend horizontally
            ),
            showlegend=True,
            xaxis_rangeslider_visible=False,
            height=800
        )

        return fig

    def performance_table(self,df, tickers):
        perform = {}

        for ticker in tickers:
            df_t = df[df['Ticker'] == ticker]
            LEN = len(df_t)
            Pct_change_1P = (df_t['Close'].iloc[-1] - df_t['Close'].iloc[0]) / df_t['Close'].iloc[0]
            Pct_change_12P = (df_t['Close'].iloc[-1] - df_t['Close'].iloc[int(LEN / 2)]) / df_t['Close'].iloc[int(LEN / 2)]
            Pct_change_14P = (df_t['Close'].iloc[-1] - df_t['Close'].iloc[int(LEN / 4)]) / df_t['Close'].iloc[int(LEN / 4)]
            Pct_change_last = (df_t['Close'].iloc[-1] - df_t['Close'].iloc[-2]) / df_t['Close'].iloc[-2]

            perform[ticker] = {
                'Last value': Pct_change_last * 100,
                '1/4 Period': Pct_change_14P * 100,
                '1/2 Period': Pct_change_12P * 100,
                '1 Period': Pct_change_1P * 100,
            }

        df_perform = pd.DataFrame(perform).rename_axis("Period").reset_index()

        header = df_perform.columns.tolist()
        # header.insert(0, 'Period')
        values = [df_perform[col] for col in df_perform.columns]
        # values.insert(0, [1, int(LEN / 4), int(LEN / 2), LEN])

        formatted_values = [[self.format_number(val) for val in row] for row in values]

        # Create the Plotly Table
        fig = go.Figure(data=[go.Table(
            header=dict(values=header,
                        #fill_color='paleturquoise',
                        align='center',
                        font=dict(size=18, weight='bold')
                        ),
            cells=dict(values=formatted_values,
                    align='center',
                    font=dict(size=16),
                    )
        )])

        fig.update_layout(
            title='Price Performance',  # Add your title here
            #title_x=0.5,  # Centers the title horizontally
            title_font=dict(size=20, family='Arial'),  # Customize the title font
            height=250,
            margin=dict(t=70, b=0, l=0, r=0)
        )
        fig.update_layout()

        return fig

    def format_number(self,val):
        if isinstance(val, float):
            if val >= 0:
                return f"<br><span style='color: green;'>+{val:.2f}%"  # Positive values with a plus sign
            else:
                return f"<br><span style='color: red;'>{val:.2f}%"  # Negative values without a sign
        else:
            return f"<b>{val}</b>"


    def plot_line_multiple(self,df, title=""):
        fig = go.Figure()

        dfs = df.groupby('Ticker')

        for df_name, df in dfs:
            fig.add_trace(go.Scatter(x=df.index,
                                    y=df['Pct_change'],
                                    mode='lines',
                                    name=f'{df_name}',
                                    meta=df_name,
                                    hovertemplate='%{meta}: %{y:.2f}<br><extra></extra>', )
                        )

        fig.add_hline(y=0, line_dash="dash")

        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Percentage change',
            hovermode='x',
            xaxis=dict(
                showspikes=True,  # Enable vertical spikes
                spikemode='across',  # Draw spikes across the entire plot
                spikesnap='cursor',  # Snap spikes to the cursor position
                showline=True,  # Show axis line
                showgrid=True,  # Show grid lines
                spikecolor='black',  # Custom color for spikes
                spikethickness=1,  # Custom thickness for spikes
                rangeslider=dict(
                    visible=True,
                    thickness=0.1
                ),
            ),
            yaxis=dict(
                tickformat='.0%',
                showspikes=True,  # Enable horizontal spikes
                spikemode='across',  # Draw spikes across the entire plot
                spikesnap='cursor',  # Snap spikes to the cursor position
                showline=True,  # Show axis line
                showgrid=True,  # Show grid lines
                spikecolor='black',  # Custom color for spikes
                spikethickness=1,  # Custom thickness for spikes
                side='right'  # Move the y-axis ticks to the right side
            ),
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",  # Aligns the legend vertically to the top
                y=-0.3,  # Positions the legend below the subplots
                xanchor="center",  # Aligns the legend horizontally to the center
                x=0.5  # Centers the legend horizontally
            ),
            showlegend=True,
            # xaxis_rangeslider_visible=True,
            height=800
        )

        return fig
    

    def plot_capital(self,df, ticker="", currency=""):

        if 'Total Debt' not in df.index:
            df.loc['Total Debt'] = df.loc['Total Liabilities Net Minority Interest']

        if 'Cash Cash Equivalents And Short Term Investments' not in df.index:
            df.loc['Cash Cash Equivalents And Short Term Investments'] = df.loc['Cash And Cash Equivalents']

        df1 = pd.concat([df.loc['Ordinary Shares Number'], df.loc['Cash Cash Equivalents And Short Term Investments'],
                        df.loc['Total Debt']], axis=1)

        df1 = df1.iloc[::-1].dropna()

        dates = df1.index
        start = dates[0]

        hist = self.data_handler.fetch_historical_data(
            ticker=ticker,
            interval='1d',
            start=start - datetime.timedelta(days=5)
        )
        df2 = hist.copy()

        df2.index = df2.index.tz_localize(None)

        merge = pd.merge_asof(df1, df2, left_index=True, right_index=True, direction='backward')

        merge['Market cap'] = merge['Close'] * merge['Ordinary Shares Number']
        merge['Enterprise Value'] = merge['Market cap'] + merge['Total Debt'] - \
                                    merge['Cash Cash Equivalents And Short Term Investments']

        df = merge.copy()

        percentages = round(df['Market cap'].astype('float64').pct_change(periods=1) * 100, 1)
        percentages = percentages.apply(lambda x: f"+{x}%" if x > 0 else ("" if pd.isna(x) else f"{x}%")).tolist()

        # Create the line chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Market cap'],
            name='Market cap',
            # base=base,
            marker=dict(
                color='green'  # Assign a color from the green color scale
            ),
            text=percentages,
            textfont=dict(size=12, color='black', family='Arial', weight='bold'),
            textposition='outside',
        ))

        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Total Debt'],
            name='Total Debt',
            base=df['Market cap'],
            marker=dict(
                color='orange'  # Assign a color from the green color scale
            )
        ))

        fig.add_trace(go.Bar(
            x=df.index,
            y=-df['Cash Cash Equivalents And Short Term Investments'],
            name='Cash',
            base=df['Market cap'] + df['Total Debt'],
            marker=dict(
                color='red'  # Assign a color from the green color scale
            )
        ))

        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Enterprise Value'],
            name='Enterprise Value',
            # base=base,
            marker=dict(
                color='blue'  # Assign a color from the green color scale
            )
        ))

        # Add titles and labels
        fig.update_layout(
            title=f'Capital structure: {ticker}',
            xaxis_title='Date',
            yaxis_title=f'Amount (in {currency})',
            # template='plotly_dark'  # Optional: use a dark theme
        )

        return fig


    def plot_capital_multiple(self,tickers, tp="Annual"):
        fig = go.Figure()

        for ticker in tickers:
            bs = self.data_handler.fetch_balance(ticker, tp=tp)
            df = bs.iloc[:, :4]
            df = df[df.columns[::-1]]
            df.columns = pd.to_datetime(df.columns).strftime('%b %d, %Y')

            df1 = bs.loc['Ordinary Shares Number'].to_frame()

            df1 = df1.iloc[::-1].dropna()

            dates = df1.index
            start = dates[0]

            hist = self.data_handler.fetch_historical_data (
                ticker=ticker,
                interval='1d',
                start=start - datetime.timedelta(days=5)
            )

            df2 = hist.copy()

            df2.index = df2.index.tz_localize(None)

            merge = pd.merge_asof(df1, df2, left_index=True, right_index=True, direction='backward')

            merge['Market cap'] = merge['Close'] * merge['Ordinary Shares Number']

            df = merge.copy()

            percentages = round(df['Market cap'].astype('float64').pct_change(periods=1) * 100, 1)
            percentages = percentages.apply(lambda x: f"+{x}%" if x > 0 else ("" if pd.isna(x) else f"{x}%")).tolist()

            df.index = pd.to_datetime(df.index).strftime('%b %d, %Y')

            fig.add_trace(go.Bar(
                x=[[ticker] * len(df.index), df.index],
                y=df['Market cap'],
                name='Market cap',
                # marker=dict(color='green'),
                text=percentages,
                textfont=dict(size=10, color='black', family='Arial', weight='bold'),
                textposition='outside',
                showlegend=False,
            ))

        # Update layout to stack bars and set titles
        fig.update_layout(
            barmode='group',
            title=f'Market Cap: {", ".join(tickers)}',
            # xaxis_title='Date',
            yaxis_title=f'Amount',
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",  # Aligns the legend vertically to the top
                y=-0.5,  # Positions the legend below the subplots
                xanchor="center",  # Aligns the legend horizontally to the center
                x=0.5  # Centers the legend horizontally
            ),
            margin=dict(t=70, b=150)
        )
        return fig

    def plot_balance(self,df, ticker="", currency=""):
        df.columns = pd.to_datetime(df.columns).strftime('%b %d, %Y')

        components = {
            'Total Assets': {
                'color': 'forestgreen',
                'name': 'Assets',
            },
            'Stockholders Equity': {
                'color': 'CornflowerBlue',  # http://davidbau.com/colors/
                'name': "Stockholder's Equity",
            },
            'Total Liabilities Net Minority Interest': {
                'color': 'tomato',
                'name': "Total Liabilities",
            },
        }
        fig = go.Figure()

        for component in components:
            if component == 'Total Assets':
                fig.add_trace(go.Bar(
                    x=[df.columns, ['Assets'] * len(df.columns)],
                    y=df.loc[component],
                    name=components[component]['name'],
                    marker=dict(color=components[component]['color'])
                ))
            else:

                fig.add_trace(go.Bar(
                    x=[df.columns, ['L+E'] * len(df.columns)],
                    y=df.loc[component],
                    name=components[component]['name'],
                    marker=dict(color=components[component]['color'])
                ))

        offset = 0.03 * df.loc['Total Assets'].max()

        for i, date in enumerate(df.columns):
            fig.add_annotation(
                x=[date, "Assets"],
                y=df.loc['Total Assets', date]/2,
                text=str(round(df.loc['Total Assets', date] / 1e9, 1)) + 'B',  # Format as text
                showarrow=False,
                font=dict(size=12, color="black"),
                align="center"
            )
            percentage = round((df.loc['Total Liabilities Net Minority Interest', date] / df.loc['Total Assets', date]) * 100, 1)
            fig.add_annotation(
                x=[date, "L+E"],
                y=df.loc['Stockholders Equity', date] + df.loc['Total Liabilities Net Minority Interest', date] / 2,
                text=str(percentage) + '%',  # Format as text
                showarrow=False,
                font=dict(size=12, color="black"),
                align="center"
            )
            if i > 0:
                percentage = round((df.loc['Total Assets'].iloc[i] / df.loc['Total Assets'].iloc[i - 1] - 1) * 100, 1)
                sign = '+' if percentage >= 0 else ''
                fig.add_annotation(
                    x=[date, "Assets"],
                    y=df.loc['Total Assets', date] + offset,
                    text=sign + str(percentage) + '%',  # Format as text
                    showarrow=False,
                    font=dict(size=12, color="black"),
                    align="center"
                )

        fig.update_layout(
            barmode='stack',
            title=f'Accounting Balance: {ticker}',
            xaxis_title='Year',
            yaxis_title=f'Amount (in {currency})',
            legend_title='Balance components',
        )

        return fig

    def plot_balance_multiple(self,TICKERS, tp="Annual"):

        fig = go.Figure()

        for ticker in TICKERS:
            bs = self.data_handler.fetch_balance(ticker, tp=tp)
            df = bs.iloc[:, :4]
            df = df[df.columns[::-1]]
            df.columns = pd.to_datetime(df.columns).strftime('%b %d, %Y')

            show_legend = ticker == TICKERS[0]

            percentages = round(df.loc['Total Assets'].astype('float64').pct_change(periods=1) * 100, 1)
            percentages = percentages.apply(lambda x: f"+{x}%" if x > 0 else ("" if pd.isna(x) else f"{x}%")).tolist()

            fig.add_trace(go.Bar(
                x=[[ticker] * len(df.columns), df.columns],
                y=df.loc['Total Assets'],
                name='Total Assets',
                marker=dict(color='forestgreen'),
                text=percentages,
                textfont=dict(size=10, color='black', family='Arial', weight='bold'),
                textposition='outside',
                showlegend=show_legend,
            ))

            fig.add_trace(go.Bar(
                x=[[ticker] * len(df.columns), df.columns],
                y=df.loc['Total Liabilities Net Minority Interest'],
                name='Total Liabilities',
                marker=dict(color='tomato'),
                showlegend=show_legend,
            ))

        # Update layout to stack bars and set titles
        fig.update_layout(
            barmode='overlay',
            title=f'Accounting Balance: {", ".join(TICKERS)}',
            #xaxis_title='Date',
            yaxis_title=f'Amount',
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",  # Aligns the legend vertically to the top
                y=-0.5,  # Positions the legend below the subplots
                xanchor="center",  # Aligns the legend horizontally to the center
                x=0.5  # Centers the legend horizontally
            ),
            margin=dict(t=70)
        )
        return fig

    def plot_income_multiple(self,TICKERS, tp="Annual"):

        fig = go.Figure()

        for ticker in TICKERS:
            ist = self.data_handler.fetch_income(ticker, tp=tp)
            df = ist.iloc[:, :4]
            df = df[df.columns[::-1]]
            df.columns = pd.to_datetime(df.columns).strftime('%b %d, %Y')

            show_legend = ticker == TICKERS[0]

            percentages = round(df.loc['Total Revenue'].astype('float64').pct_change(periods=1) * 100, 1)
            percentages = percentages.apply(lambda x: f"+{x}%" if x > 0 else ("" if pd.isna(x) else f"{x}%")).tolist()

            fig.add_trace(go.Bar(
                x=[[ticker] * len(df.columns), df.columns],
                y=df.loc['Total Revenue'],
                name='Total Revenue',
                marker=dict(color='rgb(0,68,27)'),
                text=percentages,
                textfont=dict(size=10, color='black', family='Arial', weight='bold'),
                textposition='outside',
                showlegend=show_legend,
            ))

            percentages = round(df.loc['Net Income Common Stockholders'].astype('float64').pct_change(periods=1) * 100, 1)
            percentages = percentages.apply(lambda x: f"+{x}%" if x > 0 else ("" if pd.isna(x) else f"{x}%")).tolist()

            fig.add_trace(go.Bar(
                x=[[ticker] * len(df.columns), df.columns],
                y=df.loc['Net Income Common Stockholders'],
                name='Net Income',
                marker=dict(color='rgb(224, 253, 74)'),
                text=percentages,
                textfont=dict(size=10, color='gray', family='Arial', weight='bold'),
                textposition='outside',
                showlegend=show_legend,
            ))

        # Update layout to stack bars and set titles
        fig.update_layout(
            barmode='overlay',
            title=f'Income: {", ".join(TICKERS)}',
            #xaxis_title='Date',
            yaxis_title=f'Amount',
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",  # Aligns the legend vertically to the top
                y=-0.5,  # Positions the legend below the subplots
                xanchor="center",  # Aligns the legend horizontally to the center
                x=0.5  # Centers the legend horizontally
            ),
            margin=dict(t=70)
        )
        return fig

    def plot_cash_multiple(self,TICKERS, tp="Annual"):
        cashflow = {
            'Operating Cash Flow': {
                'Alternative': ['Cash Flowsfromusedin Operating Activities Direct']
            },
        }

        fig = go.Figure()

        for ticker in TICKERS:
            cf = self.data_handler.fetch_cash(ticker, tp=tp)
            df = cf.iloc[:, :4]
            df = df[df.columns[::-1]]
            df.columns = pd.to_datetime(df.columns).strftime('%b %d, %Y')

            show_legend = ticker == TICKERS[0]

            for component in cashflow:
                if component not in df.index:
                    alternatives = cashflow[component]['Alternative']
                    for alternative in alternatives:
                        if alternative in df.index:
                            df.loc[component] = df.loc[alternative]
                            break

            percentages = round(df.loc['Operating Cash Flow'].astype('float64').pct_change(periods=1) * 100, 1)
            percentages = percentages.apply(lambda x: f"+{x}%" if x > 0 else ("" if pd.isna(x) else f"{x}%")).tolist()

            fig.add_trace(go.Bar(
                x=[[ticker] * len(df.columns), df.columns],
                y=df.loc['Operating Cash Flow'],
                name='Operating Cash Flow',
                marker=dict(color='#fec3fe'),
                text=percentages,
                textfont=dict(size=10, color='black', family='Arial', weight='bold'),
                textposition='outside',
                showlegend=show_legend,
            ))

            fig.add_trace(go.Bar(
                x=[[ticker] * len(df.columns), df.columns],
                y=df.loc['Free Cash Flow'],
                name='Free Cash Flow',
                marker=dict(color='blue'),
                showlegend=show_legend,
            ))

        # Update layout to stack bars and set titles
        fig.update_layout(
            barmode='overlay',
            title=f'Cash flow: {", ".join(TICKERS)}',
            #xaxis_title='Date',
            yaxis_title=f'Amount',
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",  # Aligns the legend vertically to the top
                y=-0.5,  # Positions the legend below the subplots
                xanchor="center",  # Aligns the legend horizontally to the center
                x=0.5  # Centers the legend horizontally
            ),
            margin=dict(t=70)
        )
        return fig

    def plot_eps(self,ticker):

        df = self.data_handlerfetch_income(ticker, tp='Annual')

        # Create the line chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df.columns,
            y=df.loc['Basic EPS'],
            mode='lines+markers',
            name='Basic EPS',
            line=dict(color='blue', width=2),
            marker=dict(size=8, color='blue')
        ))

        fig.add_trace(go.Scatter(
            x=df.columns,
            y=df.loc['Diluted EPS'],
            mode='lines+markers',
            name='Diluted EPS',
            line=dict(color='black', width=2),
            marker=dict(size=8, color='black')
        ))


        # Add titles and labels
        fig.update_layout(
            title=f'EPS: {ticker}',
            xaxis_title='Date',
            yaxis_title='EPS',
            #template='plotly_dark'  # Optional: use a dark theme
        )

        # Show the plot
        return fig

    def plot_margins(self,df, ticker):
        df = pd.concat([df.loc['Gross Profit'], df.loc['Operating Income'], df.loc['Net Income Common Stockholders'],
                        df.loc['Total Revenue']], axis=1)
        df['Gross Margin'] = df['Gross Profit'] / df['Total Revenue']
        df['Operating Margin'] = df['Operating Income'] / df['Total Revenue']
        df['Net Margin'] = df['Net Income Common Stockholders'] / df['Total Revenue']

        # Create the line chart
        fig = go.Figure()

        # Create the line chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Gross Margin'],
            mode='lines+markers',
            name='Gross Margin',
            line=dict(color='blue', width=2),
            marker=dict(size=8, color='blue')
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Operating Margin'],
            mode='lines+markers',
            name='Operating Margin',
            line=dict(color='black', width=2),
            marker=dict(size=8, color='black')
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Net Margin'],
            mode='lines+markers',
            name='Net Margin',
            line=dict(color='green', width=2),
            marker=dict(size=8, color='green')
        ))

        # Add titles and labels
        fig.update_layout(
            title=f'Profit Margins: {ticker}',
            xaxis_title='Date',
            yaxis_title='Margin',
            yaxis=dict(tickformat='.0%'),
            #template='plotly_dark'  # Optional: use a dark theme
        )

        return fig

    def plot_pe_ratio(self,ticker):
        a_is = self.data_handler.fetch_income(ticker, tp='Annual')
        q_is = self.data_handler.fetch_income(ticker, tp='Quarterly')

        eps_a = a_is.loc['Basic EPS'].iloc[::-1]
        eps_q = q_is.loc['Basic EPS'].iloc[::-1]
        eps_q = eps_q.rolling(window=4, min_periods=4).sum().dropna()
        df1 = eps_a.combine_first(eps_q)

        dates = df1.index
        start = dates[0]

        hist = self.data_handler.fetch_historical_data(
            ticker=ticker,
            interval='1d',
            start=start
        )
        df2 = hist.copy()
        df2.index = df2.index.tz_localize(None)

        merge = pd.merge_asof(df2, df1, left_index=True, right_index=True, direction='backward')
        merge['P/E ratio'] = merge['Close'] / merge['Basic EPS']

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=merge.index,
            y=merge['P/E ratio'],
            mode='lines',
            name='P/E ratio',
            line=dict(color='blue', width=2),
            #marker=dict(size=8, color='blue')
        ))

        #fig.add_hline(y=15, line_dash="dash", annotation_text='Undervalued by Graham', annotation_position="bottom right")

        fig.update_layout(
            title=f'P/E Ratio: {ticker}',
            xaxis_title='Date',
            yaxis_title='Ratio',
            #template='plotly_dark'  # Optional: use a dark theme
        )

        return fig

    def plot_assets(self,df, ticker="", currency=""):
        assests = {
            'Current Assets': {
                'Cash Cash Equivalents And Short Term Investments': {},
                'Receivables': {},
                'Prepaid Assets': None,
                'Inventory': {},
                'Hedging Assets Current': None,
                'Other Current Assets': None
            },
            'Total Non Current Assets': {
                'Net PPE': {},
                'Goodwill And Other Intangible Assets': {},
                'Investments And Advances': {},
                'Investment Properties': None,
                'Other Non Current Assets': None
            }
        }

        fig = make_subplots(
            rows=1, cols=2,
            shared_yaxes=True,  # Share x-axis for both subplots
            horizontal_spacing=0.05,  # Adjust the space between the subplots
            subplot_titles=['Current Assets', 'Non-Current Assets']  # Titles for the subplots
        )

        colors = pc.sequential.Blugrn[::-1]
        i = 0

        current_assets = 0
        for component in assests['Current Assets']:
            if component in df.index:
                current_assets += df.loc[component]
                fig.add_trace(go.Bar(
                    x=df.columns,
                    y=df.loc[component],
                    name=component,
                    marker=dict(
                        color=colors[i]  # Assign a color from the green color scale
                    ),
                    legendgroup='Current Assets',
                    showlegend=True
                ), row=1, col=1)
                i += 1

        if 'Current Assets' not in df.index:
            df.loc['Current Assets'] = current_assets

        colors = pc.sequential.Purp[::-1]
        i = 0

        non_current_assets = 0
        for component in assests['Total Non Current Assets']:
            if component in df.index:
                non_current_assets += df.loc[component]
                fig.add_trace(go.Bar(
                    x=df.columns,
                    y=df.loc[component],
                    name=component,
                    marker=dict(
                        color=colors[i]  # Assign a color from the green color scale
                    ),
                    legendgroup='Non-current Assets',
                    showlegend=True
                ), row=1, col=2)
                i += 1

        if 'Total Non Current Assets' not in df.index:
            df.loc['Total Non Current Assets'] = non_current_assets

        offset = 0.03 * max(df.loc['Current Assets'].max(), df.loc['Total Non Current Assets'].max())

        for i, date in enumerate(df.columns):
            fig.add_annotation(
                x=date,
                y=df.loc['Current Assets', date] + offset,
                text=str(round(df.loc['Current Assets', date] / 1e9, 1)) + 'B',  # Format as text
                showarrow=False,
                font=dict(size=12, color="black"),
                align="center",
                row=1, col=1
            )
            fig.add_annotation(
                x=date,
                y=df.loc['Total Non Current Assets', date] + offset,
                text=str(round(df.loc['Total Non Current Assets', date] / 1e9, 1)) + 'B',  # Format as text
                showarrow=False,
                font=dict(size=12, color="black"),
                align="center",
                row=1, col=2
            )

        # Update layout to stack bars and set titles
        fig.update_layout(
            barmode='stack',
            title=f'Assets: {ticker}',
            #xaxis1_title='Year',
            #xaxis2_title='Year',
            xaxis1=dict(
                title='Date',
                type='date',  # Ensure the x-axis is treated as a date/time axis
                tickvals=df.columns
            ),
            xaxis2=dict(
                title='Date',
                type='date',  # Ensure the x-axis is treated as a date/time axis
                tickvals=df.columns
            ),
            yaxis_title=f'Amount (in {currency})',
            # yaxis2_title=f'Amount (in {currency})',
            legend_title='Asset Components',
            # height=800
        )

        return fig

    def plot_liabilities(self,df, ticker="", currency=""):
        liabilities = {
            'Current Liabilities': {
                'Payables And Accrued Expenses': {},
                'Pensionand Other Post Retirement Benefit Plans Current': None,
                'Current Debt And Capital Lease Obligation': {},
                'Current Deferred Liabilities': {},
                'Other Current Liabilities': {}
            },
            'Total Non Current Liabilities Net Minority Interest': {
                'Long Term Debt And Capital Lease Obligation': {},
                'Non Current Deferred Liabilities': {},
                'Tradeand Other Payables Non Current': None,
                'Other Non Current Liabilities': None
            }
        }

        fig = make_subplots(
            rows=1, cols=2,
            shared_yaxes=True,  # Share x-axis for both subplots
            horizontal_spacing=0.05,  # Adjust the space between the subplots
            subplot_titles=['Current Liabilities', 'Non-Current Liabilities']  # Titles for the subplots
        )

        colors = pc.sequential.Oryel[::-1]
        i = 0

        current_liabilities = 0
        for component in liabilities['Current Liabilities']:
            if component in df.index:
                current_liabilities += df.loc[component]
                fig.add_trace(go.Bar(
                    x=df.columns,
                    y=df.loc[component],
                    name=component,
                    marker=dict(
                        color=colors[i]  # Assign a color from the green color scale
                    ),
                    legendgroup='Current Liabilities',
                    showlegend=True
                ), row=1, col=1)
                i += 1

        if 'Current Liabilities' not in df.index:
            df.loc['Current Liabilities'] = current_liabilities

        colors = pc.sequential.Brwnyl[::-1]
        i = 0
        non_current_liabilities = 0
        for component in liabilities['Total Non Current Liabilities Net Minority Interest']:
            if component in df.index:
                non_current_liabilities += df.loc[component]
                fig.add_trace(go.Bar(
                    x=df.columns,
                    y=df.loc[component],
                    name=component,
                    marker=dict(
                        color=colors[i]  # Assign a color from the green color scale
                    ),
                    legendgroup='Non-current Liabilities',
                    showlegend=True
                ), row=1, col=2)
                i += 1

        if 'Total Non Current Liabilities Net Minority Interest' not in df.index:
            df.loc['Total Non Current Liabilities Net Minority Interest'] = non_current_liabilities

        offset = 0.03 * max(df.loc['Current Liabilities'].max(),
                            df.loc['Total Non Current Liabilities Net Minority Interest'].max())

        for i, date in enumerate(df.columns):
            fig.add_annotation(
                x=date,
                y=df.loc['Current Liabilities', date] + offset,
                text=str(round(df.loc['Current Liabilities', date] / 1e9, 1)) + 'B',  # Format as text
                showarrow=False,
                font=dict(size=12, color="black"),
                align="center",
                row=1, col=1
            )
            fig.add_annotation(
                x=date,
                y=df.loc['Total Non Current Liabilities Net Minority Interest', date] + offset,
                text=str(round(df.loc['Total Non Current Liabilities Net Minority Interest', date] / 1e9, 1)) + 'B',
                # Format as text
                showarrow=False,
                font=dict(size=12, color="black"),
                align="center",
                row=1, col=2
            )

        # Update layout to stack bars and set titles
        fig.update_layout(
            barmode='stack',
            title=f'Liabilities: {ticker}',
            #xaxis1_title='Year',
            #xaxis2_title='Year',
            xaxis1=dict(
                title='Date',
                type='date',  # Ensure the x-axis is treated as a date/time axis
                tickvals=df.columns
            ),
            xaxis2=dict(
                title='Date',
                type='date',  # Ensure the x-axis is treated as a date/time axis
                tickvals=df.columns
            ),
            yaxis_title=f'Amount (in {currency})',
            # yaxis2_title=f'Amount (in {currency})',
            legend_title='Liability Components',
            # height=800
        )

        return fig

    def plot_equity(self,df, ticker="", currency=""):
        equity = {
            'Stockholders Equity': {
                'Capital Stock': {},
                'Retained Earnings': None,
                'Gains Losses Not Affecting Retained Earnings': {},
            },
        }

        fig = go.Figure()

        colors = pc.sequential.Blues[::-1]
        i = 0

        for component in equity['Stockholders Equity']:
            if component in df.index:
                fig.add_trace(go.Bar(
                    x=df.columns,
                    y=df.loc[component],
                    name=component,
                    marker=dict(
                        color=colors[i]  # Assign a color from the green color scale
                    ),
                ))
                i += 2

        offset = 0.05 * df.loc['Stockholders Equity'].max()

        for i, date in enumerate(df.columns):
            fig.add_annotation(
                x=date,
                y=df.loc['Stockholders Equity', date] + offset,
                text=str(round(df.loc['Stockholders Equity', date] / 1e9, 1)) + 'B',  # Format as text
                showarrow=False,
                font=dict(size=12, color="black"),
                align="center"
            )

        # Update layout to stack bars and set titles
        fig.update_layout(
            barmode='relative',
            title=f'Equity: {ticker}',
            # xaxis_title='Year',
            xaxis=dict(
                title='Date',
                type='date',  # Ensure the x-axis is treated as a date/time axis
                # tickformat='%Y',
                # dtick='M12'
                tickvals=df.columns
            ),
            yaxis_title=f'Amount (in {currency})',
            legend_title='Equity Components',
        )

        return fig

    def plot_income(self,df, ticker="", currency=""):
        income_st = {
            'Total Revenue': {
                'name': 'Total Revenue',
                'sign': '+',
                'base': None,
                'color': 'rgb(0,68,27)'
            },
            'Cost Of Revenue': {
                'name': 'Cost of Revenue',
                'sign': '-',
                'base': ['Total Revenue'],
                'color': 'rgb(165,15,21)'
            },
            'Gross Profit': {
                'name': 'Gross Profit',
                'sign': '+',
                'base': None,
                'color': 'rgb(35,139,69)'
            },
            'Operating Expense': {
                'name': 'Operating Expense',
                'sign': '-',
                'base': ['Gross Profit'],
                'color': 'rgb(239,59,44)'
            },
            'Operating Income': {
                'name': 'Operating Income',
                'sign': '+',
                'base': None,
                'color': 'rgb(116,196,118)'
            },
            'Net Non Operating Interest Income Expense': {
                'name': 'Net Non Operating I/E',
                'sign': '+',
                'base': ['Operating Income'],
                'color': 'rgb(130, 109, 186)'
            },
            'Other Income Expense': {
                'name': 'Other Income Expense',
                'sign': '+',
                'base': ['Operating Income', 'Net Non Operating Interest Income Expense'],
                'color': 'rgb(185, 152, 221)'
            },
            'Pretax Income': {
                'name': 'Pretax Income',
                'sign': '+',
                'base': None,
                'color': 'rgb(199,233,192)'
            },
            'Tax Provision': {
                'name': 'Tax Provision',
                'sign': '-',
                'base': ['Pretax Income'],
                'color': 'rgb(252,146,114)'
            },
            'Net Income Common Stockholders': {
                'name': 'Net Income',
                'sign': '+',
                'base': None,
                'color': 'rgb(224, 253, 74)'
            }
        }

        # Create traces for stacked data
        traces = list()

        for component in income_st:
            if component in df.index:

                sign = income_st[component]['sign']
                value = df.loc[component] if sign == '+' else -df.loc[component]

                base = income_st[component]['base']
                if base:
                    base = 0
                    for _ in income_st[component]['base']:
                        if _ in df.index:
                            base += df.loc[_]

                if component == "Total Revenue" or component == "Net Income Common Stockholders":
                    percentages = round(df.loc[component].astype('float64').pct_change(periods=-1) * 100, 1)
                    percentages = percentages.apply(
                        lambda x: f"+{x}%" if x > 0 else ("" if pd.isna(x) else f"{x}%")).tolist()
                    trace = go.Bar(
                        x=df.columns,
                        y=value,
                        name=income_st[component]['name'],
                        base=base,
                        marker=dict(
                            color=income_st[component]['color']  # Assign a color from the green color scale
                        ),
                        text=percentages,
                        textfont=dict(size=12, color='black', family='Arial', weight='bold'),
                        textposition='outside',
                    )
                else:
                    trace = go.Bar(
                        x=df.columns,
                        y=value,
                        name=income_st[component]['name'],
                        base=base,
                        marker=dict(
                            color=income_st[component]['color']  # Assign a color from the green color scale
                        )
                    )

                traces.append(trace)

        # Create the figure
        fig = go.Figure(data=traces)

        # Update layout to stack bars and set titles
        fig.update_layout(
            barmode='group',
            # barmode = 'overlay',
            title=f'Income Statement: {ticker}',
            # xaxis_title='Year',
            xaxis=dict(
                title='Date',
                type='date',  # Ensure the x-axis is treated as a date/time axis
                tickvals=df.columns
            ),
            yaxis_title=f'Amount (in {currency})',
            legend_title='I/E segregation',
        )

        return fig

    def plot_cash(self,df, ticker="", currency=""):
        cashflow = {
            'Operating Cash Flow': {
                'Alternative': ['Cash Flowsfromusedin Operating Activities Direct']
            },
            'Investing Cash Flow': {},
            'Financing Cash Flow': {},
            'End Cash Position': {
                'Changes In Cash': None,
                'Effect Of Exchange Rate Changes': None,
                'Beginning Cash Position': None
            }
        }

        for component in cashflow:
            if component not in df.index:
                alternatives = cashflow[component]['Alternative']
                for alternative in alternatives:
                    if alternative in df.index:
                        df.loc[component] = df.loc[alternative]
                        break

        fig = go.Figure()

        colors = pc.sequential.Plotly3[::-1]
        i = 0

        for component in cashflow:
            if component in df.index:
                if component == 'End Cash Position':
                    for item in cashflow[component]:
                        if item in df.index:
                            if item == 'Changes In Cash':
                                fig.add_trace(go.Scatter(
                                    x=df.columns,
                                    y=df.loc[item],
                                    mode='lines',
                                    line=dict(color='black', width=2, dash='dash'),
                                    name=item,
                                ))
                            else:
                                fig.add_trace(go.Bar(
                                    x=df.columns,
                                    y=df.loc[item],
                                    name=item,
                                    marker=dict(
                                        color=colors[i]  # Assign a color from the green color scale
                                    ),
                                ))
                                i += 2
                    fig.add_trace(go.Scatter(
                        x=df.columns,
                        y=df.loc[component],
                        mode='lines+markers',
                        line=dict(color='black', width=3),
                        name=component,
                    ))
                else:
                    fig.add_trace(go.Bar(
                        x=df.columns,
                        y=df.loc[component],
                        name=component,
                        marker=dict(
                            color=colors[i]  # Assign a color from the green color scale
                        ),
                    ))
                    i += 2

        offset = 0.08 * (df.loc['Operating Cash Flow']+df.loc['Beginning Cash Position']).max()

        for i, date in enumerate(df.columns):
            fig.add_annotation(
                x=date,
                y=df.loc['End Cash Position', date] + offset,
                text=str(round(df.loc['End Cash Position', date] / 1e9, 1)) + 'B',  # Format as text
                showarrow=False,
                font=dict(size=12, color="black"),
                align="center"
            )

        # Update layout to stack bars and set titles
        fig.update_layout(
            barmode='relative',
            title=f'Cash flow: {ticker}',
            # xaxis_title='Year',
            xaxis=dict(
                title='Date',
                type='date',  # Ensure the x-axis is treated as a date/time axis
                tickvals=df.columns
            ),
            yaxis_title=f'Amount (in {currency})',
            legend_title='Cash Flow Components',
        )

        return fig

    # PERFORMANCES




    # def plot_moving_averages(self, stock_data):
    #     ma_fig = go.Figure()
    #     ma_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], name='Close', mode='lines'))
    #     for window in [20, 50, 200]:
    #         ma_fig.add_trace(go.Scatter(
    #             x=stock_data.index,
    #             y=stock_data[f'SMA_{window}'],
    #             name=f'SMA {window}',
    #             mode='lines'
    #         ))
    #         ma_fig.add_trace(go.Scatter(
    #             x=stock_data.index,
    #             y=stock_data[f'EMA_{window}'],
    #             name=f'EMA {window}',
    #             mode='lines',
    #             line=dict(dash='dot')
    #         ))
    #     return ma_fig

    # def plot_candlestick(self, stock_data, symbol, time_range):
    #     end_date = datetime.today()
    #     time_range_options = ["5d","1m", "3m", "6m", "1y", "2y", "5y", "YTD", "max"]
    #     if time_range =='5d':
    #         start_date = end_date - timedelta(days=5)
    #     elif time_range == '1m':
    #         start_date = end_date - timedelta(days=30)
    #     elif time_range == '3m':
    #         start_date = end_date - timedelta(days=90)
    #     elif time_range == '6m':
    #         start_date = end_date - timedelta(days=180)
    #     elif time_range == '1y':
    #         start_date = end_date - timedelta(days=365)
    #     elif time_range == '2y':
    #         start_date = end_date - timedelta(days=2*365)
    #     elif time_range == '5y':
    #         start_date = end_date - timedelta(days=5*365)  # Approximate 5 years

    #     elif time_range == 'YTD':
    #         start_date = datetime(end_date.year, 1, 1)

    #     stock_data = stock_data.loc[start_date:end_date]
    #     candlestick_chart = go.Figure(data=[
    #         go.Candlestick(
    #             x=stock_data.index,
    #             open=stock_data['Open'],
    #             high=stock_data['High'],
    #             low=stock_data['Low'],
    #             close=stock_data['Close']
    #         )
    #     ])

    #     candlestick_chart.update_layout(
    #         title=f"{symbol} Candlestick Chart ({time_range})",
    #         xaxis_rangeslider_visible=False
       
    #     )
    #     return candlestick_chart

    # def plot_bollinger_bands(self, stock_data):
    #     bb_fig = go.Figure()
    #     bb_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Bollinger High'], fill=None, mode='lines', name='Bollinger High'))
    #     bb_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], fill='tonexty', mode='lines', name='Close'))
    #     bb_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Bollinger Low'], fill='tonexty', mode='lines', name='Bollinger Low'))
    #     return bb_fig

    # def plot_obv(self, stock_data):
    #     obv_fig = go.Figure()
    #     obv_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['OBV'], mode='lines', name='OBV'))
    #     return obv_fig

    # def plot_rsi(self, stock_data):
    #     rsi_fig = go.Figure()
    #     rsi_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['RSI'], name='RSI'))
    #     rsi_fig.update_layout(title="Relative Strength Index (RSI)", xaxis_title="Date", yaxis_title="RSI")
    #     return rsi_fig

    # def plot_macd(self, stock_data):
    #     macd_fig = go.Figure()
    #     macd_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['MACD'], name='MACD Line'))
    #     macd_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Signal_Line'], name='Signal Line'))
    #     macd_fig.update_layout(title="Moving Average Convergence Divergence (MACD)", xaxis_title="Date", yaxis_title="MACD")
    #     return macd_fig

    # def plot_atr(self, stock_data):
    #     atr_fig = go.Figure()
    #     atr_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['ATR'], name='ATR'))
    #     atr_fig.update_layout(title="Average True Range (ATR)", xaxis_title="Date", yaxis_title="ATR")
    #     return atr_fig

    # def plot_vwap(self, stock_data):
    #     vwap_fig = go.Figure()
    #     vwap_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['VWAP'], name='VWAP', line=dict(color='purple')))
    #     vwap_fig.update_layout(title="Volume Weighted Average Price (VWAP)", xaxis_title="Date", yaxis_title="VWAP")
    #     return vwap_fig

    # def plot_volatility(self, stock_data):
    #     vol_fig = go.Figure()
    #     vol_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Volatility'], name='Volatility'))
    #     vol_fig.update_layout(title="Historical Volatility", xaxis_title="Date", yaxis_title="Volatility")
    #     return vol_fig
    # # Additional plotting methods
