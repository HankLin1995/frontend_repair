import streamlit as st
import api
from datetime import datetime

st.subheader("新增缺失")



# --- Fetch defect categories and vendors ---
categories = api.get_defect_categories()
vendors = api.get_vendors()

category_options = {str(c.get('name', c.get('category_name', '無分類'))): c['defect_category_id'] for c in categories} if categories else {}
vendor_options = {str(v.get('vendor_name', '無廠商')): v['vendor_id'] for v in vendors} if vendors else {}

with st.form("defect_add_form"):

    st.markdown("**填寫人:** "+"郭曉明")
    st.markdown("**工程:** "+"測試工程")

    defect_description = st.text_area("缺失描述", max_chars=300)
    defect_category = st.selectbox("缺失分類", options=["(無)" if not category_options else "請選擇"] + list(category_options.keys()))
    assigned_vendor = st.selectbox("指派廠商", options=["(無)" if not vendor_options else "請選擇"] + list(vendor_options.keys()))

    submitted = st.form_submit_button("送出缺失")

    if submitted:
        # Prepare payload
        payload = {
            "project_id": st.session_state.active_project_id,
            "submitted_id": st.session_state.user_id,
            "defect_description": defect_description,
        }
        if defect_category not in ["(無)", "請選擇"]:
            payload["defect_category_id"] = category_options[defect_category]
        if assigned_vendor not in ["(無)", "請選擇"]:
            payload["assigned_vendor_id"] = vendor_options[assigned_vendor]
        # Call API
        result = api.create_defect(**payload)
        if result and not result.get("error"):
            st.success("缺失已成功新增！")
            st.balloons()
        else:
            st.error(f"新增失敗: {result.get('error', '未知錯誤')}")

