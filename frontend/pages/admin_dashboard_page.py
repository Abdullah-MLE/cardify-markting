"""Admin Dashboard Page."""
import streamlit as st
from frontend.api_client import APIClient
from frontend.dialogs.company_dialogs import add_company_dialog, edit_company_dialog, delete_company_dialog, manage_users_dialog

def render():
    st.title("Admin Dashboard")
    user = st.session_state.get('user', {})
    
    if user.get('role') != 'admin':
        st.error("Access denied. Admin role required.")
        return
        
    st.markdown("### Registered Companies")
    
    if st.button("Add New Company", icon=":material/add:"):
        add_company_dialog()
        
    companies = APIClient.get_companies()
    
    if not companies:
        st.info("No companies registered yet.")
        return
        
    for comp in companies:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.subheader(comp.get("company_name", "Unknown"))
                st.caption(f"Industry: {comp.get('industry', 'N/A')}")
                
            with col2:
                # Set as active context button
                is_active = st.session_state.get('user', {}).get('company_id') == comp['id']
                if is_active:
                    st.success("Active Context")
                else:
                    if st.button("Set as Active", key=f"set_active_{comp['id']}"):
                        st.session_state['user']['company_id'] = comp['id']
                        st.session_state['user_company_id'] = comp['id']  # keep in sync
                        st.rerun()
                        
            with col3:
                # Action menu via a popover
                with st.popover("Actions"):
                    if st.button("Edit Details", key=f"edit_comp_{comp['id']}", width="stretch"):
                        edit_company_dialog(comp['id'])
                    
                    if st.button("Data Gathering", key=f"data_comp_{comp['id']}", width="stretch"):
                        st.session_state.data_gathering_company_id = comp['id']
                        st.switch_page(st.session_state['pages_dict']['data_gathering'])
                        
                    if st.button("Manage Users", key=f"users_comp_{comp['id']}", width="stretch"):
                        manage_users_dialog(comp['id'])
                        
                    st.divider()
                    if st.button("Delete Company", key=f"del_comp_{comp['id']}", type="primary", width="stretch"):
                        delete_company_dialog(comp['id'])

render()
