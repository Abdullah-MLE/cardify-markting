"""Image Generation Page (Standalone)."""
import streamlit as st
import base64
from frontend.api_client import APIClient, API_URL
from frontend.components.guards import require_company
import requests

def render():
    st.title("Standalone Image Studio")
    
    company_id = require_company()
    if not company_id:
        return
        
    st.write("Generate standalone images not attached to any specific scheduled content.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Generation Prompt")
        prompt = st.text_area("Describe the image", height=150)
        
        templates = APIClient.get_templates(company_id)
        template_options = {t['id']: t.get('template_info', f"Template {t['id']}") for t in templates}
        template_options[None] = "No Template"
        
        selected_tpl_id = st.selectbox(
            "Apply Template", 
            options=list(template_options.keys()), 
            format_func=lambda x: template_options[x]
        )
        
        if st.button("Generate", type="primary", width="stretch"):
            if not prompt:
                st.error("Please provide a prompt.")
            else:
                with st.spinner("Generating..."):
                    resp = requests.post(
                        f"{API_URL}/content/generate_standalone",
                        json={"company_id": company_id, "prompt": prompt, "template_id": selected_tpl_id}
                    )
                    if resp.ok:
                        data = resp.json()
                        img_bytes = base64.b64decode(data["image_b64"])
                        st.session_state.last_generated_standalone = img_bytes
                        st.success("Generated!")
                    else:
                        st.error(f"Failed: {resp.text}")
                        
    with col2:
        st.subheader("Preview")
        if 'last_generated_standalone' in st.session_state:
            st.image(st.session_state.last_generated_standalone, width="stretch")
            st.download_button(
                label="Download",
                data=st.session_state.last_generated_standalone,
                file_name="generated_image.png",
                mime="image/png"
            )
        else:
            from frontend.components.image_placeholder import render_image_placeholder
            render_image_placeholder()

render()
