from turtle import width
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
        'location',             # 位置
        'defect_description',   # 缺失描述
        'category_name',        # 分類名稱
        'assigned_vendor_name', # 廠商
        'responsible_vendor_name', # 負責廠商
        'expected_completion_day', # 預計完成日期
        'urgency_class',        # 緊急程度分類
        'urgency_days',         # 剩餘天數
        'created_at',           # 建立時間
        'status' ,               # 目前狀態
        'unique_code'           # 唯一編號
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
                                    options=["全部", "🟡 改善中", "🟢 已完成", "🔴 已取消", "⚪ 等待中","🟣 待確認","🟤 未設定"],
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

@st.dialog("缺失歷史記錄",width="large")
def show_defect_history(defect_id):
    # 獲取缺失的完整信息，包括修繕歷史
    defect_detail = api.get_defect(defect_id, with_photos=True, with_marks=True, with_improvements=True, with_full_related=True)
    
    if not defect_detail:
        st.error("無法獲取缺失資訊")
        return
    
    tab1,tab2=st.tabs(["📋基本資訊","📷相關照片"])
    with tab1:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**缺失編號:** {defect_detail.get('defect_id', '—')}")
                st.markdown(f"**位置:** {defect_detail.get('location', '—')}")
                st.markdown(f"**分類:** {defect_detail.get('category_name', '—')}")
        with col2:
            st.markdown(f"**建立日期:** {pd.to_datetime(defect_detail.get('created_at', '')).strftime('%Y-%m-%d') if defect_detail.get('created_at') else '—'}")
            st.markdown(f"**指派廠商:** {defect_detail.get('assigned_vendor_name', '—')}")
            st.markdown(f"**目前狀態:** {defect_detail.get('status', '—')}")
            
        # 顯示缺失描述
        with st.container(border=True):
            st.markdown(f"**缺失描述:** {defect_detail.get('defect_description', '—')}")
        with st.container(border=True):
            imp=defect_detail['improvements']
            st.markdown(f"**修繕內容:** {imp[0].get('content')}")

        # st.markdown("---")

    with tab2:
        # 顯示相關照片

        col1,col2=st.columns(2)

        with col1:
            st.subheader("缺失照片")
            defect_photos = [photo for photo in defect_detail.get('photos', []) if photo['related_type'] == 'defect']
            if defect_photos:
                # img_cols = st.columns(3)
                for i, photo in enumerate(defect_photos):
                    # with img_cols[i % 3]:
                    st.image(f"{api.BASE_URL}{photo['image_url']}")
            else:
                st.info("無缺失照片")
            
        with col2:
            # 顯示改善照片
            st.subheader("修繕照片")
            improvement_photos = [photo for photo in defect_detail.get('photos', []) if photo['related_type'] == 'improvement']
            if improvement_photos:
                # img_cols = st.columns(3)
                for i, photo in enumerate(improvement_photos):
                    # with img_cols[i % 3]:
                        st.image(f"{api.BASE_URL}{photo['image_url']}")
            else:
                st.info("無修繕照片")

    st.markdown("---")

    col_left,col_right=st.columns(2)

    with col_left:
        if st.button("✅ 確認結果",use_container_width=True):
            api.update_defect(defect_id, {"status": "已完成"})
            st.toast("修繕已完成")
            st.rerun()

    with col_right:
        if st.button("🔄 退回重辦",use_container_width=True):
            api.update_defect(defect_id, {"status": "改善中"})
            st.toast("退回重辦")
            st.rerun()

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
        'location':'位置',
        'defect_description': '缺失描述',
        'category_name': '分類名稱',
        'assigned_vendor_name': '廠商',
        'responsible_vendor_name': '負責廠商',
        'expected_completion_day': None,#"預計完成日期",
        'urgency_class': '期限',
        'urgency_days': None,
        'created_at': None,#'建立時間',
        'status': '狀態',
        'unique_code': None
    },
    on_select="rerun",
    selection_mode="single-row"
)

st.caption("圖例說明: 🟥0日內,🟨7日內,🟩14日內,⬜️14日以上")

# 顯示選中的行
selected_rows = event.selection.rows
if selected_rows:
    col1,col2,col3=st.columns([1,1,1])

    # 編輯、刪除
    with col1:
        if st.button("📝 編輯",key="edit",use_container_width=True):
            # edit_defect_ui(selected_rows)
            pass

    with col2:
        selected_status=df_filter.iloc[selected_rows[0]]['status']
        if selected_status=="🟡 改善中":
            code = df_filter.iloc[selected_rows[0]]['unique_code']
            st.link_button(":star: 修繕",f"http://localhost:8501?defect_unique_code={code}",use_container_width=True)
        if selected_status=="🟣 待確認":
            if st.button("📜 確認",key="confirm",use_container_width=True):
                defect_id = df_filter.iloc[selected_rows[0]]['defect_id']
                show_defect_history(defect_id)

    with col3:
        if st.button("🗑️ 刪除",key="delete",use_container_width=True):
            df_selected = df_filter.iloc[selected_rows]
            delete_defects(df_selected)
    

