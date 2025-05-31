import streamlit as st
import pandas as pd
import api

if 'active_project_id' not in st.session_state:
    st.session_state.active_project_id = None

def display_projects_list():
    """Display the list of projects with actions using native Streamlit components"""
    
    # Get projects from API
    projects = api.get_projects()
    
    if not projects:
        st.info("目前沒有專案，請新增專案。")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(projects)

    # Add star emoji to active project
    if 'active_project_id' in st.session_state and st.session_state.active_project_id is not None:
        mask = df['project_id'] == st.session_state.active_project_id
        df.loc[mask, 'project_name'] = df.loc[mask, 'project_name'] + '⭐'


    # Display the dataframe
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={ 
            "project_id": "專案編號",
            "project_name": "專案名稱",
            "created_at": "建立時間",
        },
        selection_mode="single-row",  # Allow single row selection
        on_select="rerun"
    )

    # Handle selection
    if event.selection.rows:
        selected_row = event.selection.rows[0]  # Get first selected row
        selected_project = df.iloc[selected_row]
        
        if st.button("設為當前專案"):
            st.session_state.active_project_id = int(selected_project['project_id'])
            st.toast(f"已將專案 {selected_project['project_name']} 設為當前專案")

            st.rerun()


def display_projects_card():
    """Display the list of projects with actions using native Streamlit components"""
    
    # Get projects from API
    projects = api.get_projects()
    
    if not projects:
        st.info("目前沒有專案，請新增專案。")
        return
    
    # Display projects in cards
    cols = st.columns(3)  # 3 cards per row
    
    for i, project in enumerate(projects):
        with cols[i % 3]:
            # Get project details with counts
            project_details = api.get_project_with_counts(project['project_id'])
            
            # Determine if this is the active project
            is_active = st.session_state.active_project_id == project['project_id']
            
            # Create a container for the card
            with st.container(border=True):
                
                # Project title
                if is_active:
                    st.markdown(f"#### ⭐ {project['project_name']}")
                else:
                    st.markdown(f"#### {project['project_name']}")
                
                # Project metadata
                created_at = project.get('created_at', 'N/A')
                # st.caption(f"專案編號: {project['project_id']}")
                st.caption(f"建立時間: {created_at}")
                
                # Metrics in columns
                if project_details:
                    metrics_cols = st.columns(3)
                    with metrics_cols[0]:
                        st.metric("底圖", project_details.get('base_map_count', 0))
                    with metrics_cols[1]:
                        st.metric("缺失", project_details.get('defect_count', 0))
                    with metrics_cols[2]:
                        st.metric("使用者", project_details.get('user_count', 0))
                
                # Action buttons
                btn_cols = st.columns([1, 1, 1.5])
                with btn_cols[0]:
                    if st.button("編輯", key=f"edit_{project['project_id']}", use_container_width=True):
                        st.session_state['editing_project'] = project
                        st.rerun()
                with btn_cols[1]:
                    if st.button("刪除", key=f"delete_{project['project_id']}", use_container_width=True):
                        st.session_state['deleting_project'] = project
                        st.rerun()
                with btn_cols[2]:
                    if not is_active:
                        if st.button("設為當前專案", key=f"activate_{project['project_id']}", 
                                    use_container_width=True, type="primary"):
                            st.session_state['active_project_id'] = project['project_id']
                            st.toast(f"已將專案 {project['project_name']} 設為當前專案")
                            st.rerun()
                    else:
                        if st.button("設為當前專案", key=f"activate_{project['project_id']}", 
                                    use_container_width=True, type="primary",disabled=True):
                            pass
@st.dialog("新增專案")
def create_new_project():
    """Form for creating a new project"""
    
    with st.form("new_project_form"):
        project_name = st.text_input("專案名稱")
        submit_button = st.form_submit_button("建立專案")
        
        if submit_button:
            if project_name:
                result = api.create_project(project_name)
                if result:
                    st.success(f"專案 '{project_name}' 已建立")
                    st.rerun()
                else:
                    st.error("建立專案失敗")
            else:
                st.warning("請輸入專案名稱")

#============

st.header("📋 專案管理")

display_projects_card()

st.divider()

if st.button("新增專案"):
    create_new_project()