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
    'expected_completion_day', # 預計改善日期
    'status'                # 目前狀態
]
df_show = df_defects[show_columns]

st.dataframe(df_show, hide_index=True, column_config={
    'defect_id': '缺失編號',
    'previous_defect_id': '前置缺失編號',
    'defect_description': '缺失描述',
    'category_name': '分類名稱',
    'assigned_vendor_name': '廠商',
    'expected_completion_day': '預計改善日期',
    'status': '目前狀態'
})


