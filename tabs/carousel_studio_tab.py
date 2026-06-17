import streamlit as st

def render():
    st.title("Carousel Studio")
    user = st.session_state.get('user', {})

    if user.get('role') == 'admin' and not user.get('company_id'):
        st.info("Admins must select a company to manage carousels.", icon=":material/info:")
        if st.button("Go to Companies Dashboard", icon=":material/arrow_forward:"):
            st.switch_page(st.session_state['pages_dict']['admin_dashboard'])
        return

    st.info(
        "Carousel creation is now part of the **Create Content** flow. "
        "Select 'Carousel' as your content type when creating new content.",
        icon=":material/info:"
    )

    if st.button("Go to Create Content", icon=":material/add_circle:", type="primary"):
        st.session_state.create_content_type = 'carousel'
        st.session_state.create_mode = 'manual'
        st.switch_page(st.session_state['pages_dict']['create_content'])
