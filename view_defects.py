import streamlit as st
import api
import pandas as pd
# st.subheader("缺失列表")
from utils import get_urgency_class,get_status_class

# @st.cache_data
def show_project():

    project = api.get_project(st.session_state.active_project_id)

    if project:
        st.caption("工程 / "+project['project_name']+" / 缺失列表")
    else:
        st.warning("請先至工程列表選擇當前工程!")
        st.stop()

# @st.cache_data
def get_defects_df():
    defects=api.get_defects(st.session_state.active_project_id)

    df_defects=pd.DataFrame(defects)

    # 轉換日期格式以計算差異
    df_defects['created_at_dt'] = pd.to_datetime(df_defects['created_at'])

    # 轉換 expected_completion_day 為日期格式
    df_defects['expected_completion_date'] = pd.to_datetime(df_defects['expected_completion_day'])

    # 計算從今天到預計完成日的剩餘天數
    current_date = pd.Timestamp.now().normalize()
    df_defects['urgency_days'] = (df_defects['expected_completion_date'] - current_date).dt.days

    # 將負數變為0，表示已逾期
    df_defects['urgency_class'] = df_defects['urgency_days'].apply(get_urgency_class)

    # 只取需要顯示的欄位
    show_columns = [
        'defect_id',            # 缺失編號
        'previous_defect_id',   # 前置缺失編號
        'defect_description',   # 缺失描述
        'category_name',        # 分類名稱
        'assigned_vendor_name', # 廠商
        'expected_completion_day', # 預計完成日期
        'urgency_class',        # 緊急程度分類
        'urgency_days',         # 剩餘天數
        'created_at',           # 建立時間
        'status'                # 目前狀態
    ]
    # 處理 created_at 只顯示年月日
    if 'created_at' in df_defects.columns:
        df_defects['created_at'] = pd.to_datetime(df_defects['created_at']).dt.date.astype(str)

    df_show = df_defects[show_columns].copy()
    df_show['status'] = df_show['status'].apply(get_status_class)

    return df_show

def get_filter_df(df):
    
    #filter

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            search_text = st.text_input("🔍 搜尋", key="lookfor", placeholder="輸入關鍵字...")
        with col2:
            status_filter = st.selectbox("📊 狀態", 
                                    options=["全部", "🟡 改善中", "🟢 已完成", "🔴 已取消", "⚪ 等待中"],
                                    key="status_filter")
        with col3:
            category_filter = st.selectbox("🏷️ 分類", 
                                        ["全部"] + sorted(list(set(df['category_name'].dropna().tolist()))),
                                        key="category_filter")
        with col4:
            vendor_filter = st.selectbox("🏢 廠商", 
                                    ["全部"] + sorted(list(set(df['assigned_vendor_name'].dropna().tolist()))),
                                    key="vendor_filter")

    # 搜尋過濾
    if search_text:
        search_lower = search_text.lower()
        mask = (
            df['defect_description'].str.lower().str.contains(search_lower, na=False) |
            df['defect_id'].astype(str).str.contains(search_lower, na=False)
        )
        df = df[mask]

    # 狀態過濾
    if status_filter != "全部":
        df = df[df['status'] == status_filter]

    # 分類過濾
    if category_filter != "全部":
        df = df[df['category_name'] == category_filter]

    # 廠商過濾
    if vendor_filter != "全部":
        df = df[df['assigned_vendor_name'] == vendor_filter]

    # 按緊急程度排序
    df = df.sort_values(by=['urgency_days'])

    return df

@st.dialog("刪除缺失")
def delete_defects(df_selected):
    # Get defect IDs as a list
    defect_ids = df_selected['defect_id'].tolist()
    
    # Format the message based on number of selected items
    if len(defect_ids) == 1:
        st.write(f"確定要刪除缺失編號 {defect_ids[0]} 嗎？")
    else:
        st.write(f"確定要刪除以下 {len(defect_ids)} 個缺失嗎？")
        st.write(", ".join(map(str, defect_ids)))
    
    if st.button("刪除"):
        for defect_id in defect_ids:
            success = api.delete_defect(defect_id)
            if success:
                st.toast(f"已刪除缺失編號 {defect_id}")
            else:
                st.error(f"刪除缺失編號 {defect_id} 時發生錯誤")
        st.rerun()  # Refresh the page to update the list

#====== MAIN PAGE=======

show_project()

df=get_defects_df()
df_filter=get_filter_df(df.copy())

# 顯示過濾後的數據
event = st.dataframe(
    df_filter,
    hide_index=True,
    column_config={
        'defect_id': '缺失編號',
        'previous_defect_id': '前置缺失編號',
        'defect_description': '缺失描述',
        'category_name': '分類名稱',
        'assigned_vendor_name': '廠商',
        'expected_completion_day': "預計完成日期",
        'urgency_class': '期限',
        'urgency_days': None,
        'created_at': '建立時間',
        'status': '狀態'
    },
    on_select="rerun",
    selection_mode="multi-row"
)

st.markdown("圖例說明: 🟥0日內,🟧7日內,🟨14日內")

# 顯示選中的行
selected_rows = event.selection.rows
if selected_rows:
    col1,col2,col3=st.columns([1,1,1])

    # 編輯、刪除
    with col1:
        if st.button("📝 編輯",key="edit",use_container_width=True):
            edit_defect_ui(selected_rows)

    with col2:
        if st.button(":star: 修繕",key="repair",use_container_width=True):
            pass
    
    with col3:
        if st.button("🗑️ 刪除",key="delete",use_container_width=True):
            df_selected = df_filter.iloc[selected_rows]
            delete_defects(df_selected)
    

