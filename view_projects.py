import streamlit as st
import pandas as pd
import api
from datetime import datetime

# ============= 工具函數 =============

def format_date(date_str):
    """格式化日期字符串，只顯示年月日"""
    if date_str == 'N/A':
        return date_str
    
    try:
        return datetime.fromisoformat(date_str).strftime('%Y-%m-%d')
    except ValueError:
        return date_str

def generate_project_images(projects):
    """為每個工程生成唯一的隨機圖片"""
    return [f"https://picsum.photos/seed/{i*20}/600/400" for i in range(len(projects))]

# ============= 工程顯示函數 =============

def display_projects_list():
    """以表格形式顯示工程列表"""
    # 從 API 獲取工程
    projects = api.get_projects()
    
    if not projects:
        st.info("目前沒有工程，請新增工程。")
        return
    
    # 轉換為 DataFrame
    df = pd.DataFrame(projects)

    # 為當前工程添加標記
    if 'active_project_id' in st.session_state and st.session_state.active_project_id is not None:
        mask = df['project_id'] == st.session_state.active_project_id
        df.loc[mask, 'project_name'] = df.loc[mask, 'project_name'] + '✅'

    # 顯示 DataFrame
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={ 
            "project_id": "工程編號",
            "project_name": "工程名稱",
            "created_at": "建立時間",
        },
        selection_mode="single-row",
        on_select="rerun"
    )

    # 處理選擇
    if event.selection.rows:
        selected_row = event.selection.rows[0]
        selected_project = df.iloc[selected_row]
        
        if st.button("設為當前工程"):
            st.session_state.active_project_id = int(selected_project['project_id'])
            st.toast(f"已將工程 {selected_project['project_name']} 設為當前工程")
            st.rerun()

def display_projects_card():
    """以卡片形式顯示工程列表"""
    # 從 API 獲取工程
    projects = api.get_projects()
    
    if not projects:
        st.info("目前沒有工程，請新增工程。")
        return
    
    # 生成工程圖片
    project_images = generate_project_images(projects)
    
    # 顯示工程卡片
    cols = st.columns(3)  # 每行4個卡片
    
    for i, project in enumerate(projects):
        with cols[i % 3]:
            render_project_card(project, project_images[i])

def render_project_card(project, image_url):
    """渲染單個工程卡片"""
    # 確定這是否為當前工程
    is_active = st.session_state.active_project_id == project['project_id']
    
    # 創建卡片容器
    with st.container(border=True):
        # 工程圖標
        st.image(image_url)

        # 工程標題
        if is_active:
            st.markdown(f"#### ✅ {project['project_name']}")
        else:
            st.markdown(f"#### {project['project_name']}")
        
        # 工程元數據
        created_at = format_date(project.get('created_at', 'N/A'))
        st.caption(f"建立時間: {created_at}")

        # 工程狀態
        # st.badge("工程進行中", color="blue")

        # st.markdown("**角色:**" + project['role'])

        st.markdown("---")
        
        # 操作按鈕
        render_action_buttons(project, is_active)

def render_action_buttons(project, is_active):
    """渲染工程操作按鈕"""
    btn_cols = st.columns([1, 1, 1.5])
    
    # 編輯按鈕
    with btn_cols[0]:
        if st.button("📝 編輯", key=f"edit_{project['project_id']}", use_container_width=True):
            # st.session_state['editing_project'] = project
            edit_project(project)
    
    # 刪除按鈕
    with btn_cols[1]:
        if st.button("🗑️ 刪除", key=f"delete_{project['project_id']}", use_container_width=True):
            # st.session_state['deleting_project'] = project
            delete_project(project)
    
    # 設為當前工程按鈕
    with btn_cols[2]:
        if not is_active:
            if st.button("設為當前工程", key=f"activate_{project['project_id']}", use_container_width=True):
                st.session_state['active_project_id'] = project['project_id']
                st.toast(f"已將工程 {project['project_name']} 設為當前工程")
                st.rerun()
        else:
            st.button("設為當前工程", key=f"activate_{project['project_id']}", use_container_width=True, disabled=True)

# ============= 工程操作對話框 =============

@st.dialog("➕ 新增工程")
def create_new_project():
    """新增工程對話框"""
    project_name = st.text_input("工程名稱")
    submit_button = st.button("建立工程")
    
    if submit_button:
        if not project_name:
            st.warning("請輸入工程名稱")
            return
            
        try:
            result = api.create_project(project_name)
            if result:
                st.success(f"工程 '{project_name}' 已建立")
                result2=api.create_permission(result['project_id'], st.session_state.user_id, "擁有者")
                if result2:
                    st.success(f"工程 '{project_name}' 的權限已建立")
                else:
                    st.error("權限建立失敗")

                st.rerun()
            else:
                st.error("API 返回失敗結果")
        except Exception as e:
            st.error(f"建立工程時發生錯誤: {str(e)}")

@st.dialog("📝 編輯工程")
def edit_project(project):
    """編輯工程對話框"""
    
    with st.form("edit_project_form"):
        new_name = st.text_input("工程名稱", value=project['project_name'])
        submit_button = st.form_submit_button("更新工程")
        
        if submit_button:
            if not new_name:
                st.warning("請輸入工程名稱")
                return
                
            try:
                result = api.update_project(project['project_id'], new_name)
                if result:
                    st.success(f"工程 '{new_name}' 已更新")
                    st.rerun()
                else:
                    st.error("API 返回失敗結果")
            except Exception as e:
                st.error(f"更新工程時發生錯誤: {str(e)}")

@st.dialog("🗑️ 刪除工程")
def delete_project(project):
    """刪除工程對話框"""
    
    with st.form("delete_project_form"):
        st.write(f"確定要刪除工程 '{project['project_name']}' 嗎？")
        submit_button = st.form_submit_button("確認刪除")
        
        if submit_button:
            try:
                result = api.delete_project(project['project_id'])
                if result:
                    st.success(f"工程 '{project['project_name']}' 已刪除")
                    st.rerun()
                else:
                    st.error("API 返回失敗結果")
            except Exception as e:
                st.error(f"刪除工程時發生錯誤: {str(e)}")

# ============= 主頁面渲染 =============

def main():
    """主頁面渲染函數"""
    
    # 頁面標題
    st.header("📋 工程列表")
    st.caption("請將工程設為當前工程後，即可進入工程詳情頁面")
    # st.markdown("---")
    tab1,tab2=st.tabs(["卡片檢視","清單檢視"])
    with tab1:
        # 顯示工程卡片
        display_projects_card()
    with tab2:
        # 顯示工程清單
        display_projects_list()
    
    # 新增工程按鈕
    st.divider()
    if st.button("新增工程", type="primary"):
        create_new_project()

# 執行主函數
if __name__ == "__main__":
    main()