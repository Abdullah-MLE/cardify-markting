import streamlit as st
import datetime
from services import db_services
from services.workflows import content_workflows

def render():
    st.title("Create Single Post")
    user = st.session_state.get('user', {})

    if user.get('role') == 'admin' and not user.get('company_id'):
        st.info("Admins must select a company first.", icon=":material/info:")
        if st.button("Go to Companies Dashboard", icon=":material/arrow_forward:"):
            st.switch_page(st.session_state['pages_dict']['admin_dashboard'])
        return

    company_id = user.get('company_id')

    # Get the pre-selected date (from calendar or day details)
    if "selected_date" not in st.session_state or st.session_state.selected_date is None:
        st.session_state.selected_date = datetime.date.today()

    st.write("Generate a new post instantly using AI.")

    with st.form("create_single_post_form"):
        h1 = st.text_input("Main Headline (h1)")
        notes = st.text_area("Notes or specific instructions (e.g., 'Make it a carousel', 'Focus on discounts')")
        
        submitted = st.form_submit_button("Generate Text Content", type="primary")
        
        if submitted:
            if not h1:
                st.error("Please provide a headline.")
            else:
                with st.spinner("Generating post content with AI..."):
                    res = content_workflows.create_single_post(company_id, h1, notes)
                    if res.get("success"):
                        st.success("Post content generated successfully!")
                        st.session_state.editing_post = res["data"]
                        st.switch_page(st.session_state['pages_dict']['edit_content'])
                    else:
                        st.error(res.get("error"))
