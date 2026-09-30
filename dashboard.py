import streamlit as st
import pandas as pd
import altair as alt
import json
from datetime import datetime, timedelta
import os

# --- Cấu hình trang ---
st.set_page_config(page_title="K4-L3B Day 13 Dashboard", layout="wide")
st.title("📊 K4-L3B Day 13 Monitoring & LLMOps")

# --- Đường dẫn file log ---
LOG_FILE = "data/logs.jsonl"

# --- Hàm tải và xử lý dữ liệu ---
@st.cache_data(ttl=10) # Cache dữ liệu 10 giây để tăng tốc độ load
def load_data():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()

    data = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            try:
                line_data = json.loads(line)
                # Flatten JSON structure để dễ xử lý
                record = {
                    'ts': pd.to_datetime(line_data.get('ts'), utc=True),
                    'event': line_data.get('event'),
                    'latency_ms': line_data.get('latency_ms'),
                    'ttft_ms': line_data.get('ttft_ms'),
                    'cost_usd': line_data.get('cost_usd'),
                    'tokens_in': line_data.get('tokens_in'),
                    'tokens_out': line_data.get('tokens_out'),
                    'quality_score': line_data.get('quality_score'),
                    'error_type': line_data.get('payload', {}).get('detail') if line_data.get('event') == 'request_failed' else None,
                    'tool_success': line_data.get('tool_success')
                }
                data.append(record)
            except json.JSONDecodeError:
                continue
    
    df = pd.DataFrame(data)
    if df.empty:
        return df
        
    # Lọc dữ liệu trong 60 phút qua theo UTC
    cutoff_time = pd.Timestamp.now(tz='UTC') - pd.Timedelta(minutes=60)
    df = df[df['ts'] >= cutoff_time]
    return df

# --- Hàm vẽ biểu đồ (Generic) ---
def create_time_chart(df, y_field, title, unit, threshold=None, is_rate=False):
    if df.empty:
        st.warning(f"No data for {title}")
        return

    # Resample theo phút
    if is_rate:
        # Đếm số lượng request_received mỗi phút
        df_grouped = df[df['event'] == 'request_received'].set_index('ts').resample('1min').size().reset_index(name='count')
        y_label = 'Requests per Minute'
    else:
        # Tính mean hoặc sum theo phút cho các field khác
        df_grouped = df.set_index('ts').resample('1min')[y_field].mean().reset_index()
        y_label = f"Average {unit}"

    base = alt.Chart(df_grouped).encode(
        x=alt.X('ts', title='Time (UTC)', axis=alt.Axis(format='%H:%M')),
    ).properties(
        title=title
    )

    line = base.mark_line(point=True).encode(
        y=alt.Y(y_field if not is_rate else 'count', title=y_label),
        tooltip=['ts', alt.Tooltip(y_field if not is_rate else 'count', title=y_label, format='.4f')]
    )

    chart = line

    # Vẽ đường threshold nếu có
    if threshold:
        rule = alt.Chart(
            pd.DataFrame({'y': [threshold]})
        ).mark_rule(color='red', strokeDash=[5, 5]).encode(
            y='y'
        )

        text = alt.Chart(
            pd.DataFrame({
                'y': [threshold],
                'label': [f'Threshold: {threshold}']
            })
        ).mark_text(
            align='left',
            baseline='bottom',
            dx=5,
            dy=-5,
            color='red'
        ).encode(
            y='y',
            text='label'
        )

        chart = alt.layer(line, rule, text)

    st.altair_chart(chart, use_container_width=True)
# --- Hàm vẽ biểu đồ Error & Success đặc thù ---
def create_error_chart(df):
    st.subheader("Error Rate and Retrieval Success")
    if df.empty:
        st.warning("No data for Errors")
        return

    # Tính toán theo phút
    df_resampled = df.set_index('ts').resample('1min')
    
    # Request Failed rate
    req_received = df[df['event'] == 'request_received'].set_index('ts').resample('1min').size()
    req_failed = df[df['event'] == 'request_failed'].set_index('ts').resample('1min').size()
    
    error_rate = (req_failed / req_received * 100).fillna(0).reset_index(name='value')
    error_rate['type'] = 'Error Rate (%)'

    # Retrieval Success rate (trên các event có tool_success)
    # Retrieval Success rate (on events with tool_success)
    df_tool = df[df['tool_success'].notna()].copy()

    df_tool = df_tool.set_index('ts')

    tool_total = df_tool.resample('1min').size()

    tool_success = (
        df_tool[df_tool['tool_success'] == True]
        .resample('1min')
        .size()
    )

    retrieval_success = (
        (tool_success / tool_total * 100)
        .fillna(0)
        .reset_index(name='value')
    )

    retrieval_success['type'] = 'Retrieval Success (%)'
    retrieval_success = (tool_success / tool_total * 100).fillna(0).reset_index(name='value')
    retrieval_success['type'] = 'Retrieval Success (%)'

    combined_df = pd.concat([error_rate, retrieval_success])

    base = alt.Chart(combined_df).encode(
        x=alt.X('ts', title='Time (UTC)', axis=alt.Axis(format='%H:%M')),
        color='type'
    ).properties(
        title='Error Rate & Retrieval Success per Minute'
    )

    line = base.mark_line(point=True).encode(
        y=alt.Y('value', title='Percentage (%)'),
        tooltip=['ts', 'value', 'type']
    )

    # Threshold cho error rate (<= 2%)
    threshold_val = 2
    rule = alt.Chart(pd.DataFrame({'y': [threshold_val]})).mark_rule(color='red', strokeDash=[3, 3]).encode(y='y')
    
    st.altair_chart(line + rule, use_container_width=True)

    # Hiển thị lỗi chi tiết
    st.write("**Recent Errors (last 60m):**")
    errors = df[df['event'] == 'request_failed'][['ts', 'error_type', 'correlation_id']]
    if not errors.empty:
        st.dataframe(errors, use_container_width=True)
    else:
        st.info("No errors recorded.")

# --- Main Dashboard Layout ---
df = load_data()

if df.empty:
    st.warning("Waiting for data... (Running load_test.py?)")
else:
    # Row 1: Traffic & Latency
    col1, col2 = st.columns(2)
    with col1:
        create_time_chart(df, 'event', "Request Traffic", "req/min", threshold=1, is_rate=True)
    
    with col2:
        # Hiển thị P95 Latency
        p95_latency = df['latency_ms'].quantile(0.95)
        st.metric(label="Avg Latency (P95)", value=f"{p95_latency:.0f} ms", delta_color="normal")
        
        # Vẽ biểu đồ latency trung bình theo phút (thay vì percentiles phức tạp trên altair real-time)
        create_time_chart(df, 'latency_ms', "Average Latency per Minute", "ms", threshold=3000)

    # Row 2: Errors & Cost
    col3, col4 = st.columns(2)
    with col3:
        create_error_chart(df)
    
    with col4:
        total_cost = df['cost_usd'].sum()
        st.metric(label="Total Cost (Last 60m)", value=f"${total_cost:.4f}")
        create_time_chart(df, 'cost_usd', "Cost per Minute", "USD")

    # Row 3: Tokens & Quality
    col5, col6 = st.columns(2)
    with col5:
        # Tổng tokens in/out
        tokens_in = df['tokens_in'].sum()
        tokens_out = df['tokens_out'].sum()
        st.metric(label="Total Tokens In (Last 60m)", value=f"{tokens_in:,.0f}")
        st.metric(label="Total Tokens Out (Last 60m)", value=f"{tokens_out:,.0f}")
        
        # Biểu đồ tổng token mỗi phút
        df_tokens = df.set_index('ts').resample('1min')[['tokens_in', 'tokens_out']].sum().reset_index()
        df_tokens_melt = df_tokens.melt('ts', var_name='Token Type', value_name='Count')
        
        token_chart = alt.Chart(df_tokens_melt).mark_area().encode(
            x=alt.X('ts', title='Time (UTC)', axis=alt.Axis(format='%H:%M')),
            y=alt.Y('Count', title='Total Tokens'),
            color='Token Type',
            tooltip=['ts', 'Token Type', 'Count']
        ).properties(title='Token Usage per Minute')
        st.altair_chart(token_chart, use_container_width=True)

    with col6:
        avg_quality = df['quality_score'].mean()
        st.metric(label="Average Quality Score", value=f"{avg_quality:.2f}", delta_color="normal")
        create_time_chart(df, 'quality_score', "Quality Proxy (Mean) per Minute", "score", threshold=0.75)

# --- Footer ---
st.write("---")
st.caption(f"Last updated: {datetime.utcnow().strftime('%H:%M:%S')} UTC | Auto-refresh: 30s")

# Tự động refresh trang bằng JavaScript injection (cách đơn giản nhất cho Streamlit)
import time
time.sleep(30)
st.rerun()