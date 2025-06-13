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

# 計算預計改善日期
import pandas as pd
from datetime import timedelta

def calc_expected_completion_date(row):
    try:
        if pd.isna(row['created_at']) or pd.isna(row['expected_completion_day']):
            return ''
        created_date = pd.to_datetime(row['created_at'])
        return (created_date + timedelta(days=int(row['expected_completion_day']))).date().isoformat()
    except Exception:
        return ''

if 'created_at' in df_defects.columns and 'expected_completion_day' in df_defects.columns:
    df_defects['expected_completion_date'] = df_defects.apply(calc_expected_completion_date, axis=1)
else:
    df_defects['expected_completion_date'] = ''

df_show = df_defects[show_columns]

event=st.dataframe(df_show,
 hide_index=True, column_config={
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
selection_mode="multi-row")

selected_rows=event.selection.rows

if selected_rows:
    selected_defects=df_show.iloc[selected_rows]
    st.dataframe(selected_defects,hide_index=True)


