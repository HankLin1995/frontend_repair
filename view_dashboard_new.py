import streamlit as st
import pandas as pd
import numpy as np
import api
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import get_urgency_class, get_status_class

# 顯示項目標題
def show_project():
    project = api.get_project(st.session_state.active_project_id)

    if project:
        st.caption("工程 / "+project['project_name']+" / 執行儀表板")
    else:
        st.warning("請先至工程列表選擇當前工程!")
        st.stop()

# 獲取缺失數據
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
    
    # 計算修復時間（對於已完成的缺失）
    df_defects['updated_at_dt'] = pd.to_datetime(df_defects['updated_at'])
    df_defects['repair_days'] = (df_defects['updated_at_dt'] - df_defects['created_at_dt']).dt.days
    
    return df_defects

# 獲取過去30天的數據
def get_last_30_days_data(df, days=30):
    if df.empty:
        return pd.DataFrame()
    
    today = pd.Timestamp.now().normalize()
    thirty_days_ago = today - timedelta(days=days)
    
    # 過濾過去30天的數據
    df_30_days = df[df['created_at_dt'] >= thirty_days_ago].copy()
    
    return df_30_days

# 獲取每日新增和解決的缺失數量
def get_daily_defect_counts(df):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    # 確保日期列存在
    if 'created_date' not in df.columns:
        df['created_date'] = df['created_at_dt'].dt.date
    
    # 計算每日新增缺失數量
    daily_new = df.groupby('created_date').size().reset_index(name='新增數量')
    
    # 計算每日解決缺失數量（僅考慮已完成的缺失）
    df_completed = df[df['status'] == '已完成'].copy()
    if not df_completed.empty and 'updated_at_dt' in df_completed.columns:
        df_completed['completed_date'] = df_completed['updated_at_dt'].dt.date
        daily_completed = df_completed.groupby('completed_date').size().reset_index(name='解決數量')
    else:
        daily_completed = pd.DataFrame(columns=['completed_date', '解決數量'])
    
    return daily_new, daily_completed

# 在側邊欄選擇月份，並過濾數據
def filter_df_by_month(df):
    if df.empty:
        return df, None
    
    # ===== 月份篩選 =====
    # 確保 created_at 為 datetime
    if not pd.api.types.is_datetime64_any_dtype(df['created_at']):
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

    # 取得所有月份 (格式: 2024-06)
    df['month'] = df['created_at'].dt.to_period('M').astype(str)
    months = sorted(df['month'].dropna().unique(), reverse=True)

    st.sidebar.markdown("### 數據篩選")
    selected_month = st.sidebar.selectbox('選擇月份', options=['全部'] + months, index=0)

    filtered_df = df.copy()
    if selected_month != '全部':
        filtered_df = df[df['month'] == selected_month].copy()
        st.sidebar.caption(f"目前顯示: {selected_month} 月份")
    else:
        st.sidebar.caption("目前顯示: 全部月份")
    
    return filtered_df, selected_month

#===== 1.1 執行摘要儀表板 =====

def display_executive_summary(df):
    # st.markdown("## 執行摘要儀表板")
    
    if df.empty:
        st.info("目前沒有缺失資料")
        return
    
    # 獲取過去30天的數據
    df_30_days = get_last_30_days_data(df, days=30)
    
    # 計算關鍵績效指標
    total_defects = len(df)
    completed_defects = len(df[df['status'] == '已完成'])
    completion_rate = completed_defects / total_defects * 100 if total_defects > 0 else 0
    
    # 計算逾期缺失
    overdue_defects = len(df[df['is_overdue'] == True])
    overdue_rate = overdue_defects / total_defects * 100 if total_defects > 0 else 0
    
    # 計算進行中缺失
    in_progress_defects = len(df[df['status'] == '改善中'])
    
    # 計算過去30天的新增和解決缺失數量
    # 計算平均修復時間
    avg_repair_time = None
    avg_urgent_repair_time = None
    
    if 'repair_days' in df.columns:
        completed_with_days = df[(df['status'] == '已完成') & (df['repair_days'].notna())]
        if not completed_with_days.empty:
            avg_repair_time = completed_with_days['repair_days'].mean()
            
            # 計算緊急缺失的平均修復時間
            urgent_defects = completed_with_days[completed_with_days['urgency_class'].str.contains('0日內', na=False)]
            if not urgent_defects.empty:
                avg_urgent_repair_time = urgent_defects['repair_days'].mean()
    
    # 顯示KPI卡片
    st.markdown("#### 關鍵績效指標")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("總缺失數量", f"{total_defects}", delta=None, delta_color="normal", help=None, label_visibility="visible")
        st.metric("已解決缺失", f"{completed_defects} ({completion_rate:.1f}%)", delta=None, delta_color="normal", help=None, label_visibility="visible")
    
    with col2:
        st.metric("逾期缺失", f"{overdue_defects} ({overdue_rate:.1f}%)", delta=None, delta_color="normal", help=None, label_visibility="visible")
        st.metric("進行中缺失", f"{in_progress_defects}", delta=None, delta_color="normal", help=None, label_visibility="visible")
    
    with col3:
        st.metric("平均修復時間", f"{avg_repair_time:.1f} 天" if avg_repair_time and not pd.isna(avg_repair_time) else "N/A", delta=None, delta_color="normal", help=None, label_visibility="visible")
        st.metric("緊急缺失平均修復時間", f"{avg_urgent_repair_time:.1f} 天" if avg_urgent_repair_time and not pd.isna(avg_urgent_repair_time) else "N/A", delta=None, delta_color="normal", help=None, label_visibility="visible")
    # col1, col2 = st.columns(2,border=True)
    
    # with col1:
    #     st.metric("平均解決時間", f"{avg_repair_days} 天")
        
    # with col2:
    #     st.metric("緊急缺失平均處理時間", f"{avg_urgent_repair} 天")
    
    # 顯示趨勢圖
    st.markdown("### 缺失趨勢")
    
    # 顯示月份選擇說明
    if selected_month != '全部':
        st.caption(f"目前顯示 {selected_month} 月份的數據")
    
    # 獲取每日新增和解決的缺失數量
    daily_new, daily_completed = get_daily_defect_counts(filtered_df)
    
    if not daily_new.empty and not daily_completed.empty:
        # 合併數據
        daily_stats = pd.merge(daily_new, daily_completed, 
                              left_on='created_date', right_on='completed_date', 
                              how='outer').fillna(0)
        
        # 確保日期範圍完整
        if len(daily_stats) > 0:
            min_date = min(daily_stats['created_date'].min(), daily_stats['completed_date'].min())
            max_date = max(daily_stats['created_date'].max(), daily_stats['completed_date'].max())
            
            # 創建完整的日期範圍
            date_range = pd.date_range(start=min_date, end=max_date)
            date_df = pd.DataFrame({'date': date_range})
            
            # 合併到完整日期範圍
            daily_stats = pd.merge(date_df, daily_stats, 
                                  left_on='date', right_on='created_date', 
                                  how='left').fillna(0)
            
            # 計算累計值
            daily_stats['累計新增'] = daily_stats['新增數量'].cumsum()
            daily_stats['累計解決'] = daily_stats['解決數量'].cumsum()
            daily_stats['未解決數'] = daily_stats['累計新增'] - daily_stats['累計解決']
            
            # 創建趨勢圖
            fig = go.Figure()
            
            # 添加柱狀圖 - 每日新增和解決
            fig.add_trace(go.Bar(
                x=daily_stats['date'],
                y=daily_stats['新增數量'],
                name='每日新增',
                marker_color='#3498db'
            ))
            
            fig.add_trace(go.Bar(
                x=daily_stats['date'],
                y=daily_stats['解決數量'],
                name='每日解決',
                marker_color='#2ecc71'
            ))
            
            # 添加線圖 - 累計未解決
            fig.add_trace(go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['未解決數'],
                name='累計未解決',
                mode='lines+markers',
                line=dict(color='#e74c3c', width=2),
                marker=dict(size=6)
            ))
            
            # 更新布局
            fig.update_layout(
                title='缺失新增與解決趨勢',
                xaxis_title='日期',
                yaxis_title='數量',
                barmode='group',
                height=400,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("沒有足夠的數據來顯示趨勢")
    else:
        st.info("沒有足夠的數據來顯示趨勢")

#===== 1.2 廠商績效基本儀表板 =====

def display_vendor_performance(df):
    # st.markdown("## 廠商績效儀表板")
    
    if df.empty or 'assigned_vendor_name' not in df.columns:
        st.info("無廠商資料")
        return
    
    # 只針對有廠商名稱的缺失
    df_vendor = df.dropna(subset=['assigned_vendor_name']).copy()
    
    if df_vendor.empty:
        st.info("無廠商資料")
        return
    
    # 計算各廠商的缺失數量
    vendor_counts = df_vendor['assigned_vendor_name'].value_counts().reset_index()
    vendor_counts.columns = ['廠商', '缺失數量']
    
    # 計算各廠商的解決率
    vendor_group = df_vendor.groupby('assigned_vendor_name')
    vendor_stats = []
    
    for vendor, group in vendor_group:
        total = len(group)
        completed = len(group[group['status'] == '已完成'])
        overdue = len(group[group['urgency_days'] == 0])
        
        # 計算平均解決時間
        avg_repair = None
        completed_defects = group[group['status'] == '已完成']
        if not completed_defects.empty and 'repair_days' in completed_defects.columns:
            avg_repair = completed_defects['repair_days'].mean()
        
        # 計算按時完成率
        on_time_completed = len(completed_defects[completed_defects['urgency_days'] > 0])
        on_time_rate = on_time_completed / completed if completed > 0 else 0
        
        vendor_stats.append({
            '廠商': vendor,
            '總缺失數': total,
            '已解決數': completed,
            '解決率': completed / total * 100 if total > 0 else 0,
            '逾期數': overdue,
            '逾期率': overdue / total * 100 if total > 0 else 0,
            '平均解決天數': avg_repair if avg_repair is not None else None,
            '按時完成率': on_time_rate * 100
        })
    
    # 轉換為DataFrame並排序
    vendor_df = pd.DataFrame(vendor_stats)
    
    # 顯示廠商績效表格
    st.markdown("### 廠商績效指標")
    
    # 格式化數據
    formatted_df = vendor_df.copy()
    formatted_df['解決率'] = formatted_df['解決率'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
    formatted_df['逾期率'] = formatted_df['逾期率'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
    formatted_df['平均解決天數'] = formatted_df['平均解決天數'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "-")
    formatted_df['按時完成率'] = formatted_df['按時完成率'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
    
    # 顯示表格
    st.dataframe(formatted_df, use_container_width=True)
    
    # 廠商缺失數量橫向條形圖
    st.markdown("### 廠商缺失數量")
    
    # 只顯示前10名廠商
    top_vendors = vendor_df.sort_values('總缺失數', ascending=False).head(10)
    
    fig = px.bar(
        top_vendors,
        y='廠商',
        x='總缺失數',
        title='廠商缺失數量 (前10名)',
        orientation='h',
        color='解決率',
        color_continuous_scale=px.colors.sequential.Viridis,
        text='總缺失數'
    )
    
    fig.update_traces(textposition='outside')
    
    fig.update_layout(
        height=500,
        xaxis_title="缺失數量",
        yaxis_title="廠商",
        coloraxis_colorbar=dict(title="解決率 %")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 廠商解決率排名
    st.markdown("### 廠商解決率排名")
    
    # 只顯示前10名廠商（按解決率排序）
    top_vendors_by_rate = vendor_df.sort_values('解決率', ascending=False).head(10)
    
    fig = px.bar(
        top_vendors_by_rate,
        y='廠商',
        x='解決率',
        title='廠商解決率排名 (前10名)',
        orientation='h',
        color='解決率',
        color_continuous_scale=px.colors.sequential.Greens,
        text='解決率'
    )
    
    fig.update_traces(
        texttemplate='%{x:.1f}%',
        textposition='outside'
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="解決率 (%)",
        yaxis_title="廠商"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 廠商平均解決時間排名
    st.markdown("### 廠商平均解決時間排名")
    
    # 過濾掉沒有平均解決時間的廠商
    vendors_with_time = vendor_df.dropna(subset=['平均解決天數']).copy()
    
    if not vendors_with_time.empty:
        # 只顯示前10名廠商（按平均解決時間排序）
        top_vendors_by_time = vendors_with_time.sort_values('平均解決天數').head(10)
        
        fig = px.bar(
            top_vendors_by_time,
            y='廠商',
            x='平均解決天數',
            title='廠商平均解決時間排名 (前10名)',
            orientation='h',
            color='平均解決天數',
            color_continuous_scale=px.colors.sequential.Blues_r,  # 反轉顏色，使較短時間為深色
            text='平均解決天數'
        )
        
        fig.update_traces(
            texttemplate='%{x:.1f} 天',
            textposition='outside'
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="平均解決時間 (天)",
            yaxis_title="廠商"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("沒有足夠的數據來顯示平均解決時間")

#===== 1.3 缺失類型分布儀表板 =====

def display_defect_types(df):
    # st.markdown("## 缺失類型分布儀表板")
    
    if df.empty:
        st.info("目前沒有缺失資料")
        return
    
    # 缺失分類分布
    st.markdown("### 缺失分類分布")
    
    if 'category_name' in df.columns:
        # 計算各分類的缺失數量
        category_counts = df['category_name'].value_counts().reset_index()
        category_counts.columns = ['分類', '數量']
        
        # 計算百分比
        total = category_counts['數量'].sum()
        category_counts['百分比'] = category_counts['數量'] / total * 100
        
        # 只取前10個分類
        if len(category_counts) > 10:
            category_counts = category_counts.head(10)
        
        # 創建環形圖
        fig = px.pie(
            category_counts,
            values='數量',
            names='分類',
            title='缺失分類分布',
            hole=0.4,  # 環形圖中心孔的大小
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        # 添加百分比標籤
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            insidetextorientation='radial'
        )
        
        fig.update_layout(height=500)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 各分類的解決率比較
        st.markdown("### 各分類的解決率比較")
        
        # 計算各分類的解決率
        category_stats = []
        
        for category in category_counts['分類']:
            category_df = df[df['category_name'] == category]
            total = len(category_df)
            completed = len(category_df[category_df['status'] == '已完成'])
            resolution_rate = completed / total * 100 if total > 0 else 0
            
            # 計算平均解決時間
            avg_time = None
            completed_defects = category_df[category_df['status'] == '已完成']
            if not completed_defects.empty and 'repair_days' in completed_defects.columns:
                avg_time = completed_defects['repair_days'].mean()
            
            category_stats.append({
                '分類': category,
                '總數': total,
                '已解決': completed,
                '解決率': resolution_rate,
                '平均解決時間': avg_time if avg_time is not None else None
            })
        
        # 轉換為DataFrame並排序
        category_df = pd.DataFrame(category_stats).sort_values('解決率', ascending=False)
        
        # 創建解決率條形圖
        fig = px.bar(
            category_df,
            x='分類',
            y='解決率',
            title='各分類解決率比較',
            color='解決率',
            color_continuous_scale=px.colors.sequential.Viridis,
            text='解決率'
        )
        
        fig.update_traces(
            texttemplate='%{y:.1f}%',
            textposition='outside'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="分類",
            yaxis_title="解決率 (%)",
            xaxis={'categoryorder':'total descending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("沒有分類資料")
    
    # 緊急程度分布
    st.markdown("### 緊急程度分布")
    
    if 'urgency_class' in df.columns:
        # 提取緊急程度的emoji和文字
        df['urgency_text'] = df['urgency_class'].str.split(' ').str[1]
        
        # 計算各緊急程度的缺失數量
        urgency_counts = df['urgency_text'].value_counts().reset_index()
        urgency_counts.columns = ['緊急程度', '數量']
        
        # 計算百分比
        total = urgency_counts['數量'].sum()
        urgency_counts['百分比'] = urgency_counts['數量'] / total * 100
        
        # 創建堆疊柱狀圖，按緊急程度和解決狀態分析
        urgency_status = df.groupby(['urgency_text', 'status']).size().reset_index(name='數量')
        
        fig = px.bar(
            urgency_status,
            x='urgency_text',
            y='數量',
            color='status',
            title='緊急程度與解決狀態分布',
            barmode='stack',
            color_discrete_map={
                '已完成': '#2ecc71',
                '改善中': '#3498db',
                '已取消': '#95a5a6',
                '等待中': '#f39c12'
            },
            category_orders={"urgency_text": ["0日內", "7日內", "14日內", "14日以上"]}
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="緊急程度",
            yaxis_title="數量",
            legend_title="狀態"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("沒有緊急程度資料")

# 主頁面
def main():
    show_project()
    
    # 獲取缺失數據
    df = get_defects_df()
    
    # 在側邊欄進行月份篩選，並將過濾後的數據傳遞給各個儀表板函數
    filtered_df, selected_month = filter_df_by_month(df)
    
    # 如果選擇了特定月份，在主頁面顯示
    if selected_month and selected_month != '全部':
        st.caption(f"目前顯示 {selected_month} 月份的數據")
    
    # 創建標籤頁
    tab1, tab2, tab3 = st.tabs(["📊 執行摘要", "🏆 廠商績效", "📚 缺失分析"])
    
    with tab1:
        st.markdown("## 執行摘要儀表板")
        display_executive_summary(filtered_df)
    
    with tab2:
        st.markdown("## 廠商績效儀表板")
        display_vendor_performance(filtered_df)
    
    with tab3:
        st.markdown("## 缺失類型分布儀表板")
        display_defect_types(filtered_df)

if __name__ == "__main__":
    main()
