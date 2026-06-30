"""Edit Template Page."""
import streamlit as st
from frontend.api_client import APIClient
from frontend.components.guards import require_company
from frontend.components.image_placeholder import render_image_placeholder

def render():
    company_id = require_company()
    if not company_id:
        return
        
    tpl_id = st.session_state.get('edit_template_id')
    if not tpl_id:
        st.error("No template selected.")
        if st.button("Back to Templates"):
            st.switch_page(st.session_state['pages_dict']['templates'])
        return
        
    templates = APIClient.get_templates(company_id)
    tpl_matches = [t for t in templates if t['id'] == tpl_id]
    if not tpl_matches:
        st.error("Template not found.")
        return
        
    tpl = tpl_matches[0]
    
    st.title("Edit Template")
    if st.button("← Back to Templates"):
        st.session_state.edit_template_id = None
        st.switch_page(st.session_state['pages_dict']['templates'])
        
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Current Template")
        if tpl.get("template_url"):
            st.image(tpl["template_url"], width="stretch")
        else:
            render_image_placeholder()
            
        with st.form("edit_tpl_details"):
            info = st.text_input("Name/Info", value=tpl.get("template_info", ""))
            constraints = st.text_area("Usage Constraints", value=tpl.get("template_constraints", ""), height=200)
            if st.form_submit_button("Save Text Details"):
                APIClient.update_template(tpl_id, {"template_info": info, "template_constraints": constraints})
                st.success("Details updated!")
                st.rerun()
                
    with col2:
        st.subheader("AI Image Editing")
        st.write("Modify the template design using AI.")
        
        edit_notes = st.text_area("Modification Instructions", placeholder="Make the background darker, change the header color...")
        
        if st.button("Apply AI Edit", type="primary"):
            if not edit_notes:
                st.warning("Please provide instructions.")
            else:
                with st.spinner("Editing template..."):
                    res = APIClient.edit_template(tpl_id, edit_notes)
                    if res and res.get("url"):
                        APIClient.update_template(tpl_id, {"template_url": res["url"]})
                        st.success("Template edited successfully!")
                        st.rerun()

render()
