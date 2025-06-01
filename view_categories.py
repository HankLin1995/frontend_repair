import streamlit as st
import api
import pandas as pd

# ============ 新增分類 ============
@st.dialog("新增分類")
def create_category_ui():
    with st.form("create_category_form"):
        new_category_name = st.text_input("分類名稱", key="new_category_name")
        description = st.text_area("描述",value="無", key="new_category_description")
        submit_button = st.form_submit_button("新增分類")
        if submit_button:
            if not new_category_name:
                st.warning("請輸入分類名稱")
            else:
                try:
                    result = api.create_defect_category(new_category_name, description)
                    if result:
                        st.success(f"分類 '{new_category_name}' 已新增")
                        st.rerun()
                    else:
                        st.error("API 返回失敗結果")
                except Exception as e:
                    st.error(f"新增分類時發生錯誤: {str(e)}")

# ============ 編輯分類對話框 ============
@st.dialog("編輯分類")
def edit_category_ui(category):
    with st.form(f"edit_category_{category['defect_category_id']}"):
        category_name = st.text_input("分類名稱", value=category['category_name'])
        description = st.text_area("描述", value=category['description'])
        submit_button = st.form_submit_button("更新分類")
        if submit_button:
            if not category_name:
                st.warning("請輸入分類名稱")
                return
            try:
                # 這裡假設有 api.update_defect_category，若沒有可以補上
                result = api.update_defect_category(category['defect_category_id'], category_name, description)
                if result:
                    st.success(f"分類 '{category_name}' 已更新")
                    st.rerun()
                else:
                    st.error("API 返回失敗結果")
            except Exception as e:
                st.error(f"更新分類時發生錯誤: {str(e)}")

# ============ 取得分類資料 ============

categories = api.get_defect_categories() 

# ============ 顯示分類表格 ============
df = pd.DataFrame(categories)

# split 'category_list' by comma
df['category_list'] = df['category_name'].str.split('、')

if not df.empty:
    # category_names = df['category_name'].tolist()
    # selected = st.pills("分類標籤", category_names)

    event = st.dataframe(
        df,
        column_config={
            "defect_category_id": None,
            "category_name": "分類名稱",
            "description": None,
            "category_list": st.column_config.ListColumn("分類標籤"),
            "created_at": "建立時間",
        },
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    # 單列操作
    if event.selection.rows:
        selected_row = event.selection.rows[0]
        selected_category = df.iloc[selected_row]
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 編輯", key=f"edit_{selected_category['defect_category_id']}", use_container_width=True):
                edit_category_ui(selected_category)
                # st.rerun()
        with col2:
            if st.button("🗑️ 刪除", key=f"delete_{selected_category['defect_category_id']}", use_container_width=True):
                api.delete_defect_category(selected_category['defect_category_id'])
                st.rerun()
else:
    st.info("目前尚無分類資料，請新增分類。")


st.markdown("---")

if st.button("新增分類"):
    create_category_ui()
    

