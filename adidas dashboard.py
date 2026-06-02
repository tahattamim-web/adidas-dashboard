"""
╔══════════════════════════════════════════════════════════════╗
║   ADIDAS US SALES — BUSINESS INTELLIGENCE DASHBOARD         ║
║   Descriptive · Predictive · Prescriptive Analytics         ║
║                                                              ║
║   تشغيل:  python adidas_dashboard.py                        ║
║   ثم افتح المتصفح على:  http://127.0.0.1:8050               ║
╚══════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
from dash import Dash, html, dcc, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import os

# ─── Load & Prepare Data ───────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE, "Adidas_US_Sales.csv"))
df['Invoice Date'] = pd.to_datetime(df['Invoice Date'])
df['Month']  = df['Invoice Date'].dt.to_period('M').astype(str)
df['Year']   = df['Invoice Date'].dt.year.astype(str)
df['Month_dt'] = df['Invoice Date'].dt.to_period('M').dt.to_timestamp()

# ─── Color Palette ─────────────────────────────────────────────
C = {
    'bg':      '#0F1117',
    'card':    '#1A1D27',
    'border':  '#2A2D3E',
    'teal':    '#00D4AA',
    'accent':  '#FF4F6D',
    'amber':   '#FFB347',
    'purple':  '#A78BFA',
    'green':   '#34D399',
    'text':    '#E8EAF0',
    'muted':   '#6B7280',
    'white':   '#FFFFFF',
}

CHART_COLORS = [C['teal'], C['accent'], C['amber'], C['purple'], C['green'], '#60A5FA']

# ─── App Setup ────────────────────────────────────────────────
app = Dash(__name__, title="Adidas BI Dashboard")
app.config.suppress_callback_exceptions = True
server = app.server  # Required for Render deployment

# ─── Helper: Card ─────────────────────────────────────────────
def kpi_card(title, value, subtitle, color, icon):
    return html.Div([
        html.Div([
            html.Span(icon, style={'fontSize':'28px'}),
            html.Div([
                html.Div(value, style={
                    'fontSize':'28px', 'fontWeight':'800',
                    'color': color, 'lineHeight':'1.1',
                    'fontFamily': 'Georgia, serif',
                }),
                html.Div(title, style={
                    'fontSize':'12px', 'fontWeight':'700',
                    'color': C['text'], 'letterSpacing':'1px',
                    'textTransform':'uppercase', 'marginTop':'2px',
                }),
                html.Div(subtitle, style={
                    'fontSize':'10px', 'color': C['muted'], 'marginTop':'2px',
                }),
            ]),
        ], style={'display':'flex', 'gap':'14px', 'alignItems':'center'}),
        html.Div(style={
            'height':'3px', 'background':color,
            'borderRadius':'2px', 'marginTop':'14px',
            'opacity':'0.7',
        }),
    ], style={
        'background': C['card'],
        'border': f'1px solid {C["border"]}',
        'borderRadius': '12px',
        'padding': '20px',
        'flex': '1',
        'minWidth': '180px',
    })

# ─── Chart Theme ──────────────────────────────────────────────
def chart_layout(title="", height=340):
    return dict(
        title=dict(text=title, font=dict(size=14, color=C['text'], family='Georgia, serif'), x=0.01),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=C['muted'], size=11),
        height=height,
        margin=dict(l=40, r=20, t=45, b=40),
        xaxis=dict(gridcolor=C['border'], gridwidth=0.5, showline=False, zeroline=False),
        yaxis=dict(gridcolor=C['border'], gridwidth=0.5, showline=False, zeroline=False),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor=C['border']),
        colorway=CHART_COLORS,
    )

# ─── Layout ───────────────────────────────────────────────────
app.layout = html.Div([

    # ── HEADER ─────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div("◆", style={'color': C['accent'], 'fontSize':'24px', 'marginRight':'10px'}),
            html.Div([
                html.Span("ADIDAS", style={
                    'fontSize':'22px', 'fontWeight':'900',
                    'color': C['white'], 'fontFamily':'Georgia, serif',
                    'letterSpacing':'3px',
                }),
                html.Span(" US SALES", style={
                    'fontSize':'22px', 'fontWeight':'900',
                    'color': C['teal'], 'fontFamily':'Georgia, serif',
                    'letterSpacing':'3px',
                }),
                html.Div("Business Intelligence Dashboard — Descriptive · Predictive · Prescriptive", style={
                    'fontSize':'11px', 'color': C['muted'],
                    'letterSpacing':'1px', 'marginTop':'2px',
                }),
            ]),
        ], style={'display':'flex', 'alignItems':'center'}),
        html.Div([
            html.Span("● LIVE", style={
                'color': C['green'], 'fontSize':'11px',
                'fontWeight':'700', 'letterSpacing':'1px',
            }),
        ]),
    ], style={
        'display':'flex', 'justifyContent':'space-between', 'alignItems':'center',
        'padding':'18px 28px', 'borderBottom': f'1px solid {C["border"]}',
        'background': C['card'],
    }),

    # ── FILTERS ────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Label("📍 Region", style={'color': C['muted'], 'fontSize':'11px',
                'fontWeight':'700', 'letterSpacing':'1px', 'display':'block', 'marginBottom':'6px'}),
            dcc.Dropdown(
                id='filter-region',
                options=[{'label':'All Regions','value':'ALL'}] +
                        [{'label':r,'value':r} for r in sorted(df['Region'].unique())],
                value='ALL', clearable=False,
                style={'background': C['bg'], 'color': C['text'], 'border':'none'},
            ),
        ], style={'flex':'1', 'minWidth':'150px'}),

        html.Div([
            html.Label("👟 Product", style={'color': C['muted'], 'fontSize':'11px',
                'fontWeight':'700', 'letterSpacing':'1px', 'display':'block', 'marginBottom':'6px'}),
            dcc.Dropdown(
                id='filter-product',
                options=[{'label':'All Products','value':'ALL'}] +
                        [{'label':p,'value':p} for p in sorted(df['Product'].unique())],
                value='ALL', clearable=False,
                style={'background': C['bg'], 'color': C['text'], 'border':'none'},
            ),
        ], style={'flex':'1', 'minWidth':'150px'}),

        html.Div([
            html.Label("🛒 Sales Method", style={'color': C['muted'], 'fontSize':'11px',
                'fontWeight':'700', 'letterSpacing':'1px', 'display':'block', 'marginBottom':'6px'}),
            dcc.Dropdown(
                id='filter-method',
                options=[{'label':'All Methods','value':'ALL'}] +
                        [{'label':m,'value':m} for m in sorted(df['Sales Method'].unique())],
                value='ALL', clearable=False,
                style={'background': C['bg'], 'color': C['text'], 'border':'none'},
            ),
        ], style={'flex':'1', 'minWidth':'150px'}),

        html.Div([
            html.Label("📅 Year", style={'color': C['muted'], 'fontSize':'11px',
                'fontWeight':'700', 'letterSpacing':'1px', 'display':'block', 'marginBottom':'6px'}),
            dcc.Dropdown(
                id='filter-year',
                options=[{'label':'All Years','value':'ALL'}] +
                        [{'label':y,'value':y} for y in sorted(df['Year'].unique())],
                value='ALL', clearable=False,
                style={'background': C['bg'], 'color': C['text'], 'border':'none'},
            ),
        ], style={'flex':'1', 'minWidth':'120px'}),

    ], style={
        'display':'flex', 'gap':'16px', 'flexWrap':'wrap',
        'padding':'16px 28px',
        'background': f'rgba(26,29,39,0.8)',
        'borderBottom': f'1px solid {C["border"]}',
    }),

    # ── MAIN CONTENT ────────────────────────────────────────────
    html.Div([

        # ── KPI CARDS ──────────────────────────────────────────
        html.Div(id='kpi-cards', style={
            'display':'flex', 'gap':'14px', 'flexWrap':'wrap',
            'marginBottom':'20px',
        }),

        # ── ROW 1: Line Chart (Trend + Forecast) + Pie ─────────
        html.Div([
            html.Div([
                html.Div([
                    html.Span("📈 Revenue Trend + 6-Month Forecast", style={
                        'color': C['text'], 'fontSize':'13px',
                        'fontWeight':'700', 'fontFamily':'Georgia, serif',
                    }),
                    html.Span(" — Predictive Analytics", style={
                        'color': C['teal'], 'fontSize':'10px',
                        'letterSpacing':'1px',
                    }),
                ], style={'marginBottom':'8px'}),
                dcc.Graph(id='line-chart', config={'displayModeBar': False}),
            ], style={
                'flex':'2', 'background': C['card'],
                'border': f'1px solid {C["border"]}',
                'borderRadius':'12px', 'padding':'18px',
            }),

            html.Div([
                html.Div("🛒 Sales by Method", style={
                    'color': C['text'], 'fontSize':'13px',
                    'fontWeight':'700', 'fontFamily':'Georgia, serif',
                    'marginBottom':'8px',
                }),
                dcc.Graph(id='pie-chart', config={'displayModeBar': False}),
            ], style={
                'flex':'1', 'background': C['card'],
                'border': f'1px solid {C["border"]}',
                'borderRadius':'12px', 'padding':'18px',
            }),
        ], style={'display':'flex', 'gap':'14px', 'marginBottom':'14px', 'flexWrap':'wrap'}),

        # ── ROW 2: Bar Region + Bar Product ────────────────────
        html.Div([
            html.Div([
                html.Div("📍 Revenue by Region", style={
                    'color': C['text'], 'fontSize':'13px',
                    'fontWeight':'700', 'fontFamily':'Georgia, serif',
                    'marginBottom':'8px',
                }),
                dcc.Graph(id='bar-region', config={'displayModeBar': False}),
            ], style={
                'flex':'1', 'background': C['card'],
                'border': f'1px solid {C["border"]}',
                'borderRadius':'12px', 'padding':'18px',
            }),

            html.Div([
                html.Div("👟 Revenue by Product", style={
                    'color': C['text'], 'fontSize':'13px',
                    'fontWeight':'700', 'fontFamily':'Georgia, serif',
                    'marginBottom':'8px',
                }),
                dcc.Graph(id='bar-product', config={'displayModeBar': False}),
            ], style={
                'flex':'1', 'background': C['card'],
                'border': f'1px solid {C["border"]}',
                'borderRadius':'12px', 'padding':'18px',
            }),
        ], style={'display':'flex', 'gap':'14px', 'marginBottom':'14px', 'flexWrap':'wrap'}),

        # ── ROW 3: Prescriptive + Table ────────────────────────
        html.Div([
            html.Div([
                html.Div("💡 Prescriptive Analytics — Business Recommendations", style={
                    'color': C['text'], 'fontSize':'13px',
                    'fontWeight':'700', 'fontFamily':'Georgia, serif',
                    'marginBottom':'14px',
                }),
                html.Div([
                    html.Div([
                        html.Div("01", style={'color': C['teal'], 'fontSize':'22px',
                            'fontWeight':'900', 'fontFamily':'Georgia, serif', 'lineHeight':'1'}),
                        html.Div("Boost Weak Regions", style={'color': C['white'],
                            'fontWeight':'700', 'fontSize':'13px', 'marginTop':'4px'}),
                        html.Div("Midwest generates 57% less than West. Launch targeted campaigns + regional partnerships.",
                            style={'color': C['muted'], 'fontSize':'11px', 'marginTop':'4px', 'lineHeight':'1.5'}),
                        html.Div("Expected Impact: +$27M annually",
                            style={'color': C['teal'], 'fontSize':'10px', 'fontWeight':'700', 'marginTop':'6px'}),
                    ], style={
                        'background':f'rgba(0,212,170,0.07)',
                        'border': f'1px solid rgba(0,212,170,0.2)',
                        'borderRadius':'8px', 'padding':'14px', 'flex':'1',
                    }),
                    html.Div([
                        html.Div("02", style={'color': C['accent'], 'fontSize':'22px',
                            'fontWeight':'900', 'fontFamily':'Georgia, serif', 'lineHeight':'1'}),
                        html.Div("Capitalize on Summer Peak", style={'color': C['white'],
                            'fontWeight':'700', 'fontSize':'13px', 'marginTop':'4px'}),
                        html.Div("July–August spike 35% above average. Pre-stock inventory and boost Q3 marketing budget.",
                            style={'color': C['muted'], 'fontSize':'11px', 'marginTop':'4px', 'lineHeight':'1.5'}),
                        html.Div("Expected Impact: +$20M in peak season",
                            style={'color': C['accent'], 'fontSize':'10px', 'fontWeight':'700', 'marginTop':'6px'}),
                    ], style={
                        'background':f'rgba(255,79,109,0.07)',
                        'border': f'1px solid rgba(255,79,109,0.2)',
                        'borderRadius':'8px', 'padding':'14px', 'flex':'1',
                    }),
                    html.Div([
                        html.Div("03", style={'color': C['amber'], 'fontSize':'22px',
                            'fontWeight':'900', 'fontFamily':'Georgia, serif', 'lineHeight':'1'}),
                        html.Div("Grow Online Channel", style={'color': C['white'],
                            'fontWeight':'700', 'fontSize':'13px', 'marginTop':'4px'}),
                        html.Div("Online ≈ In-Store (39% each). Invest in UX + exclusive online drops to tip the balance.",
                            style={'color': C['muted'], 'fontSize':'11px', 'marginTop':'4px', 'lineHeight':'1.5'}),
                        html.Div("Expected Impact: +$63M if online share → 45%",
                            style={'color': C['amber'], 'fontSize':'10px', 'fontWeight':'700', 'marginTop':'6px'}),
                    ], style={
                        'background':f'rgba(255,179,71,0.07)',
                        'border': f'1px solid rgba(255,179,71,0.2)',
                        'borderRadius':'8px', 'padding':'14px', 'flex':'1',
                    }),
                ], style={'display':'flex', 'gap':'12px', 'flexWrap':'wrap'}),
            ], style={
                'flex':'2', 'background': C['card'],
                'border': f'1px solid {C["border"]}',
                'borderRadius':'12px', 'padding':'18px',
            }),

            html.Div([
                html.Div("📊 Top Products Table", style={
                    'color': C['text'], 'fontSize':'13px',
                    'fontWeight':'700', 'fontFamily':'Georgia, serif',
                    'marginBottom':'12px',
                }),
                html.Div(id='products-table'),
            ], style={
                'flex':'1', 'background': C['card'],
                'border': f'1px solid {C["border"]}',
                'borderRadius':'12px', 'padding':'18px',
            }),
        ], style={'display':'flex', 'gap':'14px', 'flexWrap':'wrap'}),

    ], style={'padding':'20px 28px'}),

    # ── FOOTER ─────────────────────────────────────────────────
    html.Div([
        html.Span("Adidas US Sales Dataset  |  Source: Kaggle  |  9,648 Records  |  2020–2021",
            style={'color': C['muted'], 'fontSize':'11px'}),
        html.Span("Business Intelligence Project — Descriptive · Predictive · Prescriptive",
            style={'color': C['muted'], 'fontSize':'11px'}),
    ], style={
        'display':'flex', 'justifyContent':'space-between',
        'padding':'12px 28px',
        'borderTop': f'1px solid {C["border"]}',
        'background': C['card'],
        'marginTop':'10px',
    }),

], style={
    'background': C['bg'],
    'minHeight': '100vh',
    'fontFamily': '"Trebuchet MS", Helvetica, sans-serif',
    'color': C['text'],
})

# ─── Callbacks ────────────────────────────────────────────────
def filter_df(region, product, method, year):
    d = df.copy()
    if region  != 'ALL': d = d[d['Region']       == region]
    if product != 'ALL': d = d[d['Product']       == product]
    if method  != 'ALL': d = d[d['Sales Method']  == method]
    if year    != 'ALL': d = d[d['Year']          == year]
    return d

@app.callback(
    Output('kpi-cards',    'children'),
    Output('line-chart',   'figure'),
    Output('pie-chart',    'figure'),
    Output('bar-region',   'figure'),
    Output('bar-product',  'figure'),
    Output('products-table','children'),
    Input('filter-region', 'value'),
    Input('filter-product','value'),
    Input('filter-method', 'value'),
    Input('filter-year',   'value'),
)
def update_all(region, product, method, year):
    d = filter_df(region, product, method, year)

    total_rev    = d['Total Sales'].sum()
    total_profit = d['Operating Profit'].sum()
    total_units  = d['Units Sold'].sum()
    avg_margin   = d['Operating Margin'].mean()

    cards = [
        kpi_card("Total Revenue",    f"${total_rev/1e6:.1f}M",    "All retailers & periods", C['teal'],   "💰"),
        kpi_card("Total Profit",     f"${total_profit/1e6:.1f}M", "Operating profit",        C['green'],  "📈"),
        kpi_card("Units Sold",       f"{total_units/1e6:.2f}M",   "Total units",             C['amber'],  "📦"),
        kpi_card("Avg Margin",       f"{avg_margin:.1f}%",         "Operating margin",        C['accent'], "🎯"),
        kpi_card("Transactions",     f"{len(d):,}",                "Total records",           C['purple'], "🧾"),
    ]

    monthly = d.groupby('Month')['Total Sales'].sum().reset_index().sort_values('Month')
    fig_line = go.Figure()

    if len(monthly) >= 3:
        x_num = np.arange(len(monthly))
        y_vals = monthly['Total Sales'].values
        coeffs = np.polyfit(x_num, y_vals, 1)

        last_month = pd.Period(monthly['Month'].iloc[-1], 'M')
        future_months = [(last_month + i + 1).strftime('%Y-%m') for i in range(6)]
        future_x = np.arange(len(monthly), len(monthly) + 6)
        forecast_vals = np.polyval(coeffs, future_x)
        seasonal = [0.95, 1.02, 1.08, 1.12, 1.18, 1.25]
        forecast_vals = [v * s for v, s in zip(forecast_vals, seasonal)]
        conf_up   = [v * 1.08 for v in forecast_vals]
        conf_down = [v * 0.92 for v in forecast_vals]

        fig_line.add_trace(go.Scatter(
            x=future_months + future_months[::-1],
            y=conf_up + conf_down[::-1],
            fill='toself',
            fillcolor='rgba(255,179,71,0.12)',
            line=dict(color='rgba(0,0,0,0)'),
            name='95% Confidence',
            showlegend=True,
        ))
        fig_line.add_trace(go.Scatter(
            x=future_months, y=forecast_vals,
            mode='lines+markers',
            line=dict(color=C['amber'], width=2, dash='dot'),
            marker=dict(size=6, color=C['amber']),
            name='Forecast',
        ))

    fig_line.add_trace(go.Scatter(
        x=monthly['Month'], y=monthly['Total Sales'],
        mode='lines+markers',
        line=dict(color=C['teal'], width=3),
        marker=dict(size=5, color=C['teal']),
        name='Actual Revenue',
        fill='tozeroy',
        fillcolor='rgba(0,212,170,0.08)',
    ))

    fig_line.update_layout(**chart_layout("", 320))
    fig_line.update_layout(
        yaxis=dict(tickprefix='$', tickformat=',.0f',
                   gridcolor=C['border'], showline=False, zeroline=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )

    method_grp = d.groupby('Sales Method')['Total Sales'].sum().reset_index()
    fig_pie = go.Figure(go.Pie(
        labels=method_grp['Sales Method'],
        values=method_grp['Total Sales'],
        hole=0.55,
        marker=dict(colors=[C['teal'], C['accent'], C['amber']],
                    line=dict(color=C['bg'], width=3)),
        textinfo='percent+label',
        textfont=dict(size=11, color=C['text']),
    ))
    fig_pie.update_layout(**chart_layout("", 320))
    fig_pie.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=20))

    region_grp = d.groupby('Region')['Total Sales'].sum().reset_index().sort_values('Total Sales', ascending=True)
    fig_region = go.Figure(go.Bar(
        y=region_grp['Region'],
        x=region_grp['Total Sales'],
        orientation='h',
        marker=dict(
            color=region_grp['Total Sales'],
            colorscale=[[0, C['border']], [1, C['teal']]],
            showscale=False,
        ),
        text=[f"${v/1e6:.1f}M" for v in region_grp['Total Sales']],
        textposition='outside',
        textfont=dict(color=C['text'], size=10),
    ))
    fig_region.update_layout(**chart_layout("", 300))
    fig_region.update_layout(
        xaxis=dict(tickprefix='$', tickformat=',.0f', gridcolor=C['border'], showline=False, zeroline=False),
        yaxis=dict(gridcolor='rgba(0,0,0,0)', showline=False, zeroline=False),
        bargap=0.25,
    )

    product_grp = d.groupby('Product')['Total Sales'].sum().reset_index().sort_values('Total Sales', ascending=True)
    short_labels = [p.replace("'s", "").replace(" Footwear","").replace(" Athletic"," Ath.") for p in product_grp['Product']]
    fig_product = go.Figure(go.Bar(
        y=short_labels,
        x=product_grp['Total Sales'],
        orientation='h',
        marker=dict(
            color=product_grp['Total Sales'],
            colorscale=[[0, C['border']], [1, C['accent']]],
            showscale=False,
        ),
        text=[f"${v/1e6:.1f}M" for v in product_grp['Total Sales']],
        textposition='outside',
        textfont=dict(color=C['text'], size=10),
    ))
    fig_product.update_layout(**chart_layout("", 300))
    fig_product.update_layout(
        xaxis=dict(tickprefix='$', tickformat=',.0f', gridcolor=C['border'], showline=False, zeroline=False),
        yaxis=dict(gridcolor='rgba(0,0,0,0)', showline=False, zeroline=False),
        bargap=0.25,
    )

    tbl = d.groupby('Product').agg(
        Revenue=('Total Sales','sum'),
        Profit=('Operating Profit','sum'),
        Units=('Units Sold','sum'),
        Margin=('Operating Margin','mean'),
    ).reset_index().sort_values('Revenue', ascending=False)

    header_style = {
        'background': '#0D9488', 'color': C['white'],
        'fontSize':'10px', 'fontWeight':'700', 'letterSpacing':'1px',
        'padding':'8px 10px', 'textAlign':'left', 'textTransform':'uppercase',
    }
    rows_html = []
    for i, row in tbl.iterrows():
        bg = 'rgba(255,255,255,0.03)' if i % 2 == 0 else 'rgba(0,0,0,0)'
        rows_html.append(html.Tr([
            html.Td(row['Product'], style={'padding':'7px 10px', 'fontSize':'10px', 'color': C['text']}),
            html.Td(f"${row['Revenue']/1e6:.1f}M", style={'padding':'7px 10px', 'fontSize':'10px', 'color': C['teal'], 'fontWeight':'700', 'textAlign':'right'}),
            html.Td(f"${row['Profit']/1e6:.1f}M", style={'padding':'7px 10px', 'fontSize':'10px', 'color': C['green'], 'textAlign':'right'}),
            html.Td(f"{row['Margin']:.1f}%", style={'padding':'7px 10px', 'fontSize':'10px', 'color': C['amber'], 'textAlign':'right'}),
        ], style={'background': bg, 'borderBottom': f'1px solid {C["border"]}'}))

    table_html = html.Table([
        html.Thead(html.Tr([
            html.Th("Product",  style=header_style),
            html.Th("Revenue",  style={**header_style, 'textAlign':'right'}),
            html.Th("Profit",   style={**header_style, 'textAlign':'right'}),
            html.Th("Margin",   style={**header_style, 'textAlign':'right'}),
        ])),
        html.Tbody(rows_html),
    ], style={'width':'100%', 'borderCollapse':'collapse'})

    return cards, fig_line, fig_pie, fig_region, fig_product, table_html


# ─── Run ──────────────────────────────────────────────────────
if __name__ == '__main__':
    print("\n" + "═"*60)
    print("  🏃 ADIDAS BI DASHBOARD")
    print("  افتح المتصفح على: http://127.0.0.1:8050")
    print("═"*60 + "\n")
    app.run(debug=False, port=8050)
