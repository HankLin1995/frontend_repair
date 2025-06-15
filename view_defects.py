import streamlit as st
import api
import pandas as pd
# st.subheader("缺失列表")

project = api.get_project(st.session_state.active_project_id)

if project:
    st.caption("工程 / "+project['project_name']+" / 缺失列表")
else:
    st.warning("請先至工程列表選擇當前工程!")
    st.stop()

defects=api.get_defects(st.session_state.active_project_id)

df_defects=pd.DataFrame(defects)

# 只取需要顯示的欄位
show_columns = [
    'defect_id',            # 缺失編號
    'previous_defect_id',   # 前置缺失編號
    'defect_description',   # 缺失描述
    'category_name',        # 分類名稱
    'assigned_vendor_name', # 廠商
    'expected_completion_day', # 預計改善天數
    'created_at', # 建立時間
    'status'                # 目前狀態
]
# 處理 created_at 只顯示年月日
if 'created_at' in df_defects.columns:
    df_defects['created_at'] = pd.to_datetime(df_defects['created_at']).dt.date.astype(str)

df_show = df_defects[show_columns]


#filter

with st.container(border=True):
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        search_text = st.text_input("🔍 搜尋", key="lookfor", placeholder="輸入關鍵字...")
    with col2:
        status_filter = st.selectbox("📊 狀態", 
                                  options=["全部", "改善中", "已完成", "已取消"],
                                  key="status_filter")
    with col3:
        category_filter = st.selectbox("🏷️ 分類", 
                                     ["全部"] + sorted(list(set(df_show['category_name'].dropna().tolist()))),
                                     key="category_filter")
    with col4:
        vendor_filter = st.selectbox("🏢 廠商", 
                                   ["全部"] + sorted(list(set(df_show['assigned_vendor_name'].dropna().tolist()))),
                                   key="vendor_filter")

# 應用過濾條件
filtered_df = df_show.copy()

# 搜尋過濾
if search_text:
    search_lower = search_text.lower()
    mask = (
        filtered_df['defect_description'].str.lower().str.contains(search_lower, na=False) |
        filtered_df['defect_id'].astype(str).str.contains(search_lower, na=False)
    )
    filtered_df = filtered_df[mask]

# 狀態過濾
if status_filter != "全部":
    filtered_df = filtered_df[filtered_df['status'] == status_filter]

# 分類過濾
if category_filter != "全部":
    filtered_df = filtered_df[filtered_df['category_name'] == category_filter]

# 廠商過濾
if vendor_filter != "全部":
    filtered_df = filtered_df[filtered_df['assigned_vendor_name'] == vendor_filter]

# 顯示過濾後的數據
event = st.dataframe(
    filtered_df,
    hide_index=True,
    column_config={
        'defect_id': '缺失編號',
        'previous_defect_id': '前置缺失編號',
        'defect_description': '缺失描述',
        'category_name': '分類名稱',
        'assigned_vendor_name': '廠商',
        'expected_completion_day': "預計改善日期",
        'created_at': '建立時間',
        'status': '目前狀態'
    },
    on_select="rerun",
    selection_mode="multi-row"
)

# 顯示選中的行
selected_rows = event.selection.rows
if selected_rows:
    selected_defects = filtered_df.iloc[selected_rows]
    st.dataframe(selected_defects, hide_index=True)


