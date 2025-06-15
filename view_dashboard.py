import streamlit as st
import pandas as pd
import numpy as np
import api
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import get_urgency_class, get_status_class

# @st.cache_data
def show_project():
    project = api.get_project(st.session_state.active_project_id)

    if project:
        st.caption("工程 / "+project['project_name']+" / 儀表板")
    else:
        st.warning("請先至工程列表選擇當前工程!")
        st.stop()

# @st.cache_data
def get_defects_df():
    defects = api.get_defects(st.session_state.active_project_id)
    if not defects:
        return pd.DataFrame()
        
    df_defects = pd.DataFrame(defects)
    
    # 轉換日期格式
    df_defects['created_at_dt'] = pd.to_datetime(df_defects['created_at'])
    df_defects['created_date'] = df_defects['created_at_dt'].dt.date
    
    # 轉換 expected_completion_day 為日期格式
    df_defects['expected_completion_date'] = pd.to_datetime(df_defects['expected_completion_day'])
    
    # 計算從今天到預計完成日的剩餘天數
    current_date = pd.Timestamp.now().normalize()
    df_defects['urgency_days'] = (df_defects['expected_completion_date'] - current_date).dt.days
    
    # 將負數變為0，表示已逾期
    df_defects['urgency_days'] = df_defects['urgency_days'].apply(lambda x: max(0, x) if pd.notna(x) else 999)
    df_defects['urgency_class'] = df_defects['urgency_days'].apply(get_urgency_class)
    
    # 處理狀態
    df_defects['status_class'] = df_defects['status'].apply(get_status_class)
    
    return df_defects

def display_metrics(df):
    if df.empty:
        st.info("目前沒有缺失資料")
        return
        
    # 計算各種指標
    total_defects = len(df)
    completed_defects = len(df[df['status'] == '已完成'])
    in_progress_defects = len(df[df['status'] == '改善中'])
    overdue_defects = len(df[df['urgency_days'] == 0])
    
    # 計算完成率
    completion_rate = completed_defects / total_defects * 100 if total_defects > 0 else 0
    
    # 顯示指標
    col1, col2, col3, col4 = st.columns(4,border=True)
    
    with col1:
        st.metric("總缺失數量", total_defects)
        
    with col2:
        st.metric("已完成缺失", completed_defects, 
                 f"{completion_rate:.1f}%")
        
    with col3:
        st.metric("改善中缺失", in_progress_defects)
        
    with col4:
        st.metric("已逾期缺失", overdue_defects, 
                 overdue_defects, delta_color="inverse")

def display_status_chart(df):
    if df.empty:
        return
        
    # 計算各狀態的缺失數量
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['狀態', '數量']
    
    # 創建圓餅圖
    fig = px.pie(
        status_counts, 
        values='數量', 
        names='狀態',
        title='缺失狀態分布',
        color_discrete_sequence=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#95a5a6']
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def display_urgency_chart(df):
    if df.empty:
        return
        
    # 提取緊急程度的emoji和文字
    df['urgency_text'] = df['urgency_class'].str.split(' ').str[1]
    
    # 計算各緊急程度的缺失數量
    urgency_counts = df['urgency_text'].value_counts().reset_index()
    urgency_counts.columns = ['緊急程度', '數量']
    
    # 創建條形圖
    fig = px.bar(
        urgency_counts, 
        x='緊急程度', 
        y='數量',
        title='缺失緊急程度分布',
        color_discrete_sequence=['#9b59b6']
    )
    
    fig.update_layout(height=400)
    
    return fig

def display_category_chart(df):
    if df.empty:
        return
        
    # 計算各分類的缺失數量
    category_counts = df['category_name'].value_counts().reset_index()
    category_counts.columns = ['分類', '數量']
    
    # 只取前10個分類
    if len(category_counts) > 10:
        category_counts = category_counts.head(10)
    
    # 創建水平條形圖
    fig = px.bar(
        category_counts, 
        y='分類', 
        x='數量',
        title='缺失分類分布 (前10名)',
        orientation='h',
        color_discrete_sequence=['#3498db']
    )
    
    fig.update_layout(height=400)
    
    return fig

def display_vendor_chart(df):
    if df.empty:
        return
        
    # 計算各廠商的缺失數量
    vendor_counts = df['assigned_vendor_name'].value_counts().reset_index()
    vendor_counts.columns = ['廠商', '數量']
    
    # 只取前10個廠商
    if len(vendor_counts) > 10:
        vendor_counts = vendor_counts.head(10)
    
    # 創建水平條形圖
    fig = px.bar(
        vendor_counts, 
        y='廠商', 
        x='數量',
        title='廠商缺失分布 (前10名)',
        orientation='h',
        color_discrete_sequence=['#2ecc71']
    )
    
    fig.update_layout(height=400)
    
    return fig

def display_time_trend(df):
    if df.empty:
        return
        
    # 確保有創建日期
    if 'created_date' not in df.columns:
        df['created_date'] = pd.to_datetime(df['created_at']).dt.date
    
    # 計算每天的缺失數量
    daily_counts = df.groupby('created_date').size().reset_index()
    daily_counts.columns = ['日期', '新增缺失數']
    
    # 創建時間趨勢圖
    fig = px.line(
        daily_counts, 
        x='日期', 
        y='新增缺失數',
        title='缺失數量趨勢',
        markers=True,
        line_shape='linear',
        color_discrete_sequence=['#3498db']
    )
    
    fig.update_layout(height=400)
    
    return fig

def display_completion_trend(df):
    if df.empty or len(df) < 2:
        return
    
    # 計算累計缺失數和已完成缺失數
    df_sorted = df.sort_values('created_at_dt')
    dates = sorted(df_sorted['created_date'].unique())
    
    cumulative_total = []
    cumulative_completed = []
    
    for date in dates:
        # 截至該日期的所有缺失
        df_until_date = df_sorted[df_sorted['created_date'] <= date]
        total = len(df_until_date)
        completed = len(df_until_date[df_until_date['status'] == '已完成'])
        
        cumulative_total.append(total)
        cumulative_completed.append(completed)
    
    # 創建趨勢圖
    fig = go.Figure()
    
    # 添加總缺失數曲線
    fig.add_trace(go.Scatter(
        x=dates, 
        y=cumulative_total,
        mode='lines+markers',
        name='累計缺失總數',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # 添加已完成缺失數曲線
    fig.add_trace(go.Scatter(
        x=dates, 
        y=cumulative_completed,
        mode='lines+markers',
        name='累計已完成',
        line=dict(color='#2ca02c', width=2)
    ))
    
    # 添加未完成缺失數曲線
    cumulative_incomplete = [t - c for t, c in zip(cumulative_total, cumulative_completed)]
    fig.add_trace(go.Scatter(
        x=dates, 
        y=cumulative_incomplete,
        mode='lines+markers',
        name='累計未完成',
        line=dict(color='#d62728', width=2)
    ))
    
    fig.update_layout(
        title='缺失完成趨勢',
        xaxis_title='日期',
        yaxis_title='缺失數量',
        height=400
    )
    
    return fig

def display_vendor_performance(df):
    if df.empty or 'assigned_vendor_name' not in df.columns:
        st.info("無廠商資料")
        return

    # 只針對有廠商名稱的缺失
    vendor_group = df.groupby('assigned_vendor_name')
    vendor_stats = []
    for vendor, group in vendor_group:
        total = len(group)
        completed = group[group['status'] == '已完成']
        overdue = group[group['urgency_class'].str.contains('逾期')]
        avg_repair = None
        if not completed.empty and 'created_at_dt' in completed.columns and 'updated_at' in completed.columns:
            completed['updated_at_dt'] = pd.to_datetime(completed['updated_at'])
            completed['repair_days'] = (completed['updated_at_dt'] - completed['created_at_dt']).dt.days
            avg_repair = completed['repair_days'].mean()
        vendor_stats.append({
            '廠商': vendor,
            '總缺失': total,
            '完成率': len(completed) / total * 100 if total else 0,
            '逾期數': len(overdue),
            '平均修復天數': avg_repair if avg_repair is not None else '-'
        })
    perf_df = pd.DataFrame(vendor_stats).sort_values('完成率', ascending=False).head(10)
    st.subheader("🏆 廠商績效指標 (前10名)")
    st.dataframe(perf_df.style.format({'完成率': '{:.1f}%', '平均修復天數': '{:.1f}'}), use_container_width=True)

    # 可選：條形圖視覺化
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=perf_df['廠商'],
        x=perf_df['完成率'],
        name='完成率(%)',
        orientation='h',
        marker_color='#2ecc71'
    ))
    fig.add_trace(go.Bar(
        y=perf_df['廠商'],
        x=perf_df['逾期數'],
        name='逾期數',
        orientation='h',
        marker_color='#e74c3c'
    ))
    fig.update_layout(barmode='stack', title='廠商完成率與逾期數')
    st.plotly_chart(fig, use_container_width=True)

# def display_category_performance(df):
#     if df.empty or 'category_name' not in df.columns:
#         st.info("無分類資料")
#         return

#     cat_group = df.groupby('category_name')
#     cat_stats = []
#     for cat, group in cat_group:
#         total = len(group)
#         completed = group[group['status'] == '已完成']
#         avg_repair = None
#         if not completed.empty and 'created_at_dt' in completed.columns and 'updated_at' in completed.columns:
#             completed['updated_at_dt'] = pd.to_datetime(completed['updated_at'])
#             completed['repair_days'] = (completed['updated_at_dt'] - completed['created_at_dt']).dt.days
#             avg_repair = completed['repair_days'].mean()
#         cat_stats.append({
#             '分類': cat,
#             '總缺失': total,
#             '完成率': len(completed) / total * 100 if total else 0,
#             '平均修復天數': avg_repair if avg_repair is not None else '-'
#         })
#     cat_df = pd.DataFrame(cat_stats).sort_values('總缺失', ascending=False).head(10)
#     st.subheader("📚 缺失分類績效 (前10名)")
#     st.dataframe(cat_df.style.format({'完成率': '{:.1f}%', '平均修復天數': '{:.1f}'}), use_container_width=True)

#     # 條形圖
#     fig = go.Figure()
#     fig.add_trace(go.Bar(
#         y=cat_df['分類'],
#         x=cat_df['總缺失'],
#         name='缺失數量',
#         orientation='h',
#         marker_color='#3498db'
#     ))
#     fig.add_trace(go.Bar(
#         y=cat_df['分類'],
#         x=cat_df['完成率'],
#         name='完成率(%)',
#         orientation='h',
#         marker_color='#2ecc71'
#     ))
#     fig.update_layout(barmode='group', title='分類缺失數量與完成率')
#     st.plotly_chart(fig, use_container_width=True)

# ====== MAIN PAGE =======

show_project()

# 獲取缺失數據
df = get_defects_df()

# 顯示主要指標
st.subheader('📊 缺失統計指標')
display_metrics(df)

# 分兩列顯示圖表
# col1, col2 = st.columns(2,border=True)

# with col1:
#     # st.plotly_chart(display_status_chart(df), use_container_width=True)
#     st.plotly_chart(display_category_chart(df), use_container_width=True)

# with col2:
#     # st.plotly_chart(display_urgency_chart(df), use_container_width=True)
#     st.plotly_chart(display_vendor_chart(df), use_container_width=True)

tab1, tab2, tab3 = st.tabs(["📊 總覽", "🏆 廠商績效", "📚 分類分析"])
with tab1:
    # display_metrics(df)
    st.plotly_chart(display_category_chart(df), use_container_width=True)
    st.plotly_chart(display_vendor_chart(df), use_container_width=True)
with tab2:
    display_vendor_performance(df)
with tab3:
    display_category_performance(df)