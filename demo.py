import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Link Google Sheet đã publish ở định dạng CSV
CSV_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vS9aPfWcoa-pCiRgelT6zcQalosoDyfCd6KRCaQ1WZmttGQiXaTwwmpUAPJmngJUEnEJDrHGZvVuwLI/pub?output=csv'

# Khởi tạo app Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Dashboard Phân Tích Nhu Cầu Cứu Hộ"

# Định nghĩa một số style chung để tái sử dụng
COMMON_STYLES = {
    'card_container': {
        'flex': '1',
        'padding': '15px',
        'backgroundColor': 'white',
        'borderRadius': '8px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.12)',
        'margin': '5px',
        'minWidth': '200px',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center'
    },
    'card_title': {
        'margin': '0',
        'textAlign': 'center',
        'fontSize': '14px',
        'fontWeight': 'bold',
        'color': '#666',
        'textTransform': 'uppercase',
        'marginBottom': '8px'
    },
    'card_value': {
        'margin': '0',
        'textAlign': 'center',
        'fontSize': '28px',
        'fontWeight': 'bold',
        'color': '#2c3e50',
        'marginBottom': '5px'
    },
    'card_unit': {
        'margin': '0',
        'textAlign': 'center',
        'fontSize': '12px',
        'color': '#666'
    },
    'chart_container': {
        'flex': '1',
        'backgroundColor': 'white',
        'borderRadius': '8px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.12)',
        'padding': '15px',
        'margin': '5px',
        'minHeight': '350px'
    }
}

# Hàm load data từ Google Sheet
def fetch_data():
    try:
        df = pd.read_csv(CSV_URL)
        # Đổi tên cột để khớp với dữ liệu
        df.columns = ['Khu vuc', 'Nhu cau cuu ho', 'Nhu cau thiet yeu', 'Thoi gian phat sinh', 'Phan loai', 'Thanh cong']
        
        # Chuyển đổi kiểu dữ liệu
        df['Thoi gian phat sinh'] = pd.to_datetime(df['Thoi gian phat sinh'], format='%d/%m/%Y')
        df['Nhu cau cuu ho'] = pd.to_numeric(df['Nhu cau cuu ho'], errors='coerce').fillna(0)
        df['Nhu cau thiet yeu'] = pd.to_numeric(df['Nhu cau thiet yeu'], errors='coerce').fillna(0)
        # Không cần chuyển đổi Thanh cong nữa vì sẽ so sánh trực tiếp với "Yes"
        return df
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu: {str(e)}")
        return pd.DataFrame(columns=['Khu vuc', 'Nhu cau cuu ho', 'Nhu cau thiet yeu', 'Thoi gian phat sinh', 'Phan loai', 'Thanh cong'])

# Cập nhật layout của app
app.layout = html.Div([
    # Header với các KPI chính
    html.Div([
        # KPI Cards
        html.Div([
            # Tổng số lượt cứu trợ
            html.Div([
                html.H3("TỔNG SỐ LƯỢT CỨU TRỢ", style=COMMON_STYLES['card_title']),
                html.H2(id='total-rescue', style=COMMON_STYLES['card_value']),
                html.P("lượt", style=COMMON_STYLES['card_unit'])
            ], style=COMMON_STYLES['card_container']),
            
            # Tỉ lệ cứu trợ thành công
            html.Div([
                html.H3("TỈ LỆ CỨU TRỢ THÀNH CÔNG", style=COMMON_STYLES['card_title']),
                html.H2(id='success-rate', style=COMMON_STYLES['card_value']),
                html.P("%", style=COMMON_STYLES['card_unit'])
            ], style=COMMON_STYLES['card_container']),
            
            # Số trường hợp khẩn cấp
            html.Div([
                html.H3("TRƯỜNG HỢP KHẨN CẤP", style=COMMON_STYLES['card_title']),
                html.H2(id='emergency-cases', style=COMMON_STYLES['card_value']),
                html.P("trường hợp", style=COMMON_STYLES['card_unit'])
            ], style=COMMON_STYLES['card_container']),
            
            # Sửa lại card thứ 4
            html.Div([
                html.H3("KHẨN CẤP CỨU HỘ THÀNH CÔNG", style=COMMON_STYLES['card_title']),
                html.H2(id='emergency-success', style=COMMON_STYLES['card_value']),
                html.P("trường hợp", style=COMMON_STYLES['card_unit'])
            ], style=COMMON_STYLES['card_container']),
            
            # Bộ lọc
            html.Div([
                html.H3("BỘ LỌC", style=COMMON_STYLES['card_title']),
                html.Div([
                    dcc.Dropdown(
                        id='area-filter',
                        options=[],
                        multi=True,
                        placeholder="Tất cả khu vực",
                        style={
                            'width': '100%',
                            'marginBottom': '10px'
                        }
                    ),
                    dcc.DatePickerRange(
                        id='date-range',
                        display_format='DD/MM/YYYY',
                        style={'width': '100%'}
                    )
                ], style={'width': '100%'})
            ], style={**COMMON_STYLES['card_container'], 'alignItems': 'stretch'})
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'gap': '10px',
            'marginBottom': '20px',
            'flexWrap': 'nowrap'
        }),
    ]),
    
    # Charts section
    html.Div([
        # First row of charts
        html.Div([
            html.Div([
                dcc.Graph(
                    id='area-distribution',
                    style={'height': '100%'}
                )
            ], style=COMMON_STYLES['chart_container']),
            
            html.Div([
                dcc.Graph(
                    id='needs-comparison',
                    style={'height': '100%'}
                )
            ], style=COMMON_STYLES['chart_container'])
        ], style={
            'display': 'flex',
            'gap': '10px',
            'marginBottom': '10px',
            'height': '350px'
        }),
        
        # Second row of charts
        html.Div([
            html.Div([
                dcc.Graph(
                    id='time-trend',
                    style={'height': '100%'}
                )
            ], style=COMMON_STYLES['chart_container']),
            
            html.Div([
                dcc.Graph(
                    id='heatmap-chart',
                    style={'height': '100%'}
                )
            ], style=COMMON_STYLES['chart_container'])
        ], style={
            'display': 'flex',
            'gap': '10px',
            'height': '350px'
        })
    ]),
    
    dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0)
], style={
    'padding': '20px',
    'backgroundColor': '#f0f2f5',
    'minHeight': '100vh',
    'maxWidth': '1800px',
    'margin': '0 auto'
})

# Cập nhật dropdown khu vực
@app.callback(
    Output('area-filter', 'options'),
    Input('interval-component', 'n_intervals')
)
def update_area_dropdown(n):
    df = fetch_data()
    if df.empty:
        return []
    areas = sorted(df['Khu vuc'].unique())
    return [{'label': area, 'value': area} for area in areas]

# Cập nhật date picker
@app.callback(
    [Output('date-range', 'min_date_allowed'),
     Output('date-range', 'max_date_allowed'),
     Output('date-range', 'start_date'),
     Output('date-range', 'end_date')],
    Input('interval-component', 'n_intervals')
)
def update_date_picker(n):
    df = fetch_data()
    if df.empty:
        today = datetime.now()
        return today, today, today, today
    
    min_date = df['Thoi gian phat sinh'].min()
    max_date = df['Thoi gian phat sinh'].max()
    return min_date, max_date, min_date, max_date

# Cập nhật biểu đồ phân bố theo khu vực
@app.callback(
    Output('area-distribution', 'figure'),
    [Input('area-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('interval-component', 'n_intervals')]
)
def update_area_distribution(selected_areas, start_date, end_date, n):
    df = fetch_data()
    if df.empty:
        return go.Figure().add_annotation(text="Không có dữ liệu", showarrow=False)
    
    if start_date and end_date:
        df = df[(df['Thoi gian phat sinh'] >= start_date) & (df['Thoi gian phat sinh'] <= end_date)]
    
    if selected_areas:
        df = df[df['Khu vuc'].isin(selected_areas)]
    
    if df.empty:
        return go.Figure().add_annotation(text="Không có dữ liệu cho bộ lọc đã chọn", showarrow=False)
    
    # Tính tổng theo khu vực
    df_grouped = df.groupby('Khu vuc')['Nhu cau cuu ho'].sum().reset_index()
    
    fig = px.pie(df_grouped, names='Khu vuc', values='Nhu cau cuu ho',
                 title='Phân Bố Nhu Cầu Cứu Hộ Theo Khu Vực')
    return fig

# Cập nhật biểu đồ so sánh nhu cầu
@app.callback(
    Output('needs-comparison', 'figure'),
    [Input('area-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('interval-component', 'n_intervals')]
)
def update_needs_comparison(selected_areas, start_date, end_date, n):
    df = fetch_data()
    if df.empty:
        return go.Figure().add_annotation(text="Không có dữ liệu", showarrow=False)
    
    if start_date and end_date:
        df = df[(df['Thoi gian phat sinh'] >= start_date) & (df['Thoi gian phat sinh'] <= end_date)]
    
    if selected_areas:
        df = df[df['Khu vuc'].isin(selected_areas)]
    
    if df.empty:
        return go.Figure().add_annotation(text="Không có dữ liệu cho bộ lọc đã chọn", showarrow=False)
    
    # Tính tổng theo khu vực
    df_grouped = df.groupby('Khu vuc').agg({
        'Nhu cau cuu ho': 'sum',
        'Nhu cau thiet yeu': 'sum'
    }).reset_index()
    
    fig = go.Figure(data=[
        go.Bar(name='Nhu Cầu Cứu Hộ', x=df_grouped['Khu vuc'], y=df_grouped['Nhu cau cuu ho']),
        go.Bar(name='Nhu Cầu Thiết Yếu', x=df_grouped['Khu vuc'], y=df_grouped['Nhu cau thiet yeu'])
    ])
    
    fig.update_layout(
        title='So Sánh Nhu Cầu Cứu Hộ và Nhu Cầu Thiết Yếu',
        barmode='group',
        xaxis_title='Khu Vực',
        yaxis_title='Số Lượng'
    )
    return fig

# Cập nhật biểu đồ xu hướng theo thời gian
@app.callback(
    Output('time-trend', 'figure'),
    [Input('area-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('interval-component', 'n_intervals')]
)
def update_time_trend(selected_areas, start_date, end_date, n):
    df = fetch_data()
    if df.empty:
        return go.Figure().add_annotation(text="Không có dữ liệu", showarrow=False)
    
    if start_date and end_date:
        df = df[(df['Thoi gian phat sinh'] >= start_date) & (df['Thoi gian phat sinh'] <= end_date)]
    
    if selected_areas:
        df = df[df['Khu vuc'].isin(selected_areas)]
    
    if df.empty:
        return go.Figure().add_annotation(text="Không có dữ liệu cho bộ lọc đã chọn", showarrow=False)
    
    # Nhóm theo ngày và tính tổng
    df_daily = df.groupby('Thoi gian phat sinh').agg({
        'Nhu cau cuu ho': 'sum',
        'Nhu cau thiet yeu': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_daily['Thoi gian phat sinh'],
        y=df_daily['Nhu cau cuu ho'],
        name='Nhu Cầu Cứu Hộ',
        mode='lines+markers'
    ))
    fig.add_trace(go.Scatter(
        x=df_daily['Thoi gian phat sinh'],
        y=df_daily['Nhu cau thiet yeu'],
        name='Nhu Cầu Thiết Yếu',
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title='Xu Hướng Nhu Cầu Theo Thời Gian',
        xaxis_title='Thời Gian',
        yaxis_title='Số Lượng Nhu Cầu'
    )
    return fig

# Thêm callback cho biểu đồ heat map
@app.callback(
    Output('heatmap-chart', 'figure'),
    [Input('area-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('interval-component', 'n_intervals')]
)
def update_heatmap(selected_areas, start_date, end_date, n):
    df = fetch_data()
    if df.empty:
        return go.Figure().add_annotation(text="Không có dữ liệu", showarrow=False)
    
    if start_date and end_date:
        df = df[(df['Thoi gian phat sinh'] >= start_date) & (df['Thoi gian phat sinh'] <= end_date)]
    
    if selected_areas:
        df = df[df['Khu vuc'].isin(selected_areas)]
    
    if df.empty:
        return go.Figure().add_annotation(text="Không có dữ liệu cho bộ lọc đã chọn", showarrow=False)
    
    # Tạo pivot table để chuẩn bị dữ liệu cho heatmap
    df['Ngay'] = df['Thoi gian phat sinh'].dt.strftime('%d/%m/%Y')
    heatmap_data = df.pivot_table(
        values='Nhu cau cuu ho',
        index='Khu vuc',
        columns='Ngay',
        aggfunc='sum',
        fill_value=0
    )
    
    # Tạo biểu đồ heatmap với màu đỏ-vàng
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale=[
            [0, '#FFEB83'],      # Vàng nhạt cho giá trị thấp nhất
            [0.4, '#FFB443'],    # Vàng đậm cho giá trị trung bình thấp
            [0.7, '#FF4D4D'],    # Đỏ nhạt cho giá trị trung bình cao
            [1, '#B50000']       # Đỏ đậm cho giá trị cao nhất
        ],
        colorbar=dict(
            title='Số lượng<br>Nhu cầu<br>Cứu hộ',
            tickfont=dict(size=10),
            titlefont=dict(size=12)
        )
    ))
    
    fig.update_layout(
        title='Heat Map Nhu Cầu Cứu Hộ theo Khu Vực và Thời Gian',
        xaxis_title='Thời Gian',
        yaxis_title='Khu Vực',
        xaxis={'tickangle': 45},
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig

# Cập nhật callback để tính toán các KPI mới
@app.callback(
    [Output('total-rescue', 'children'),
     Output('success-rate', 'children'),
     Output('emergency-cases', 'children'),
     Output('emergency-success', 'children')],
    [Input('area-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('interval-component', 'n_intervals')]
)
def update_kpis(selected_areas, start_date, end_date, n):
    df = fetch_data()
    if df.empty:
        return "0", "0,00", "0", "0"
    
    # Lọc dữ liệu theo thời gian và khu vực
    mask = slice(None)
    if start_date and end_date:
        mask = (df['Thoi gian phat sinh'] >= start_date) & (df['Thoi gian phat sinh'] <= end_date)
    if selected_areas:
        mask = mask & (df['Khu vuc'].isin(selected_areas)) if mask is not slice(None) else df['Khu vuc'].isin(selected_areas)
    
    df = df[mask]
    
    # Tính toán các KPI
    total_rescue = len(df)
    
    # Tỉ lệ thành công tổng thể
    yes_no_mask = df['Thanh cong'].isin(['Yes', 'No'])
    success_rate = (df[yes_no_mask]['Thanh cong'] == 'Yes').mean() * 100
    
    # Các trường hợp khẩn cấp
    emergency_df = df[df['Phan loai'] == 'Emergency']
    emergency_cases = len(emergency_df)
    emergency_success = len(emergency_df[emergency_df['Thanh cong'] == 'Yes'])
    
    return (
        f"{total_rescue:,}",
        f"{success_rate:.2f}",
        f"{emergency_cases:,}",
        f"{emergency_success:,}"
    )

if __name__ == '__main__':
    app.run(debug=True, port=8050)