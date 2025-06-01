import streamlit as st
import api
import pandas as pd
import time

@st.dialog("新增廠商")
def create_vendor_ui():
    with st.form("create_vendor_form"):
        vendor_name = st.text_input("廠商名稱")
        contact_person = st.text_input("聯絡人")
        phone = st.text_input("電話")
        email=st.text_input("電子郵件")
        line_id=st.text_input("Line ID")
        responsibilities = st.text_input("負責範圍")
        submit_button = st.form_submit_button("新增廠商")
        
        if submit_button:
            if not vendor_name:
                st.warning("請輸入廠商名稱")
                return
            
            try:
                result = api.create_vendor(vendor_name, contact_person, phone, email , line_id , responsibilities)
                if result:
                    st.success(f"廠商 '{vendor_name}' 已新增")
                    st.rerun()
                else:
                    st.error("API 返回失敗結果")
            except Exception as e:
                st.error(f"新增廠商時發生錯誤: {str(e)}")

@st.dialog("編輯廠商")
def edit_vendor_ui(vendor):
    with st.form("edit_vendor_form"):
        vendor_name = st.text_input("廠商名稱", value=vendor['vendor_name'])
        contact_person = st.text_input("聯絡人", value=vendor['contact_person'])
        phone = st.text_input("電話", value=vendor['phone'])
        email=st.text_input("電子郵件", value=vendor['email'])
        line_id=st.text_input("Line ID", value=vendor['line_id'])
        responsibilities = st.text_input("負責範圍", value=vendor['responsibilities'])
        submit_button = st.form_submit_button("更新廠商")
        
        if submit_button:
            if not vendor_name:
                st.warning("請輸入廠商名稱")
                return
            
            try:
                result = api.update_vendor(vendor['vendor_id'], vendor_name, contact_person, phone,email,line_id, responsibilities)
                if result:
                    st.success(f"廠商 '{vendor_name}' 已更新")
                    st.rerun()
                else:
                    st.error("API 返回失敗結果")
            except Exception as e:
                st.error(f"更新廠商時發生錯誤: {str(e)}")

st.subheader("廠商管理")

vendors = api.get_vendors()

with st.container(border=True):
    col1,col2=st.columns([2,1])

    with col1:
        search_option=st.text_input("搜尋",key="vendor_search")
    with col2:
        filter_option=st.selectbox("篩選",options=["全部"]+list(set([v['responsibilities'] for v in vendors])),key="vendor_filter")

    if search_option:
        vendors=[v for v in vendors if search_option.lower() in v['vendor_name'].lower()]
    if filter_option != "全部":
        vendors=[v for v in vendors if v['responsibilities'] == filter_option]


df=pd.DataFrame(vendors)

event=st.dataframe(
    df,
    column_config={
        "vendor_id": None,
        "contact_person":"聯絡人",
        "phone":"電話",
        "responsibilities":"負責範圍",
        "vendor_name": "廠商名稱",
    },
    hide_index=True,
    selection_mode="single-row",
    on_select="rerun",
    use_container_width=True
)

if event.selection.rows:
    selected_row = event.selection.rows[0]
    selected_vendor = df.iloc[selected_row]
    
    if st.button("編輯",key=f"edit_{selected_vendor['vendor_id']}"):
        edit_vendor_ui(selected_vendor)

st.markdown("---")

if st.button("新增廠商"):
    create_vendor_ui()



