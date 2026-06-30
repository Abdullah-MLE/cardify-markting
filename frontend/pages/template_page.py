"""Template Management Page."""
import streamlit as st
from frontend.api_client import APIClient
from frontend.components.guards import require_company

def render():
    st.title("Templates")
    
    company_id = require_company()
    if not company_id:
        return
        
    st.write("Manage visual templates for your brand.")
    
    with st.expander("➕ Create New Template"):
        tab1, tab2 = st.tabs(["From Image (Extract)", "From Text Prompt"])
        
        with tab1:
            st.write("Extract a template from an existing post design.")
            
            upload_col, url_col = st.columns(2)
            with upload_col:
                uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"])
            with url_col:
                post_url = st.text_input("OR Image URL")
                
            instructions = st.text_area("Extraction Instructions", placeholder="Optional instructions...", height=100)
            
            if st.button("Analyze & Generate Template", type="primary", width="stretch"):
                if not post_url and not uploaded_file:
                    st.error("Please provide an image URL or upload an image.")
                else:
                    with st.spinner("Analyzing and Generating Template..."):
                        final_url = post_url
                        if uploaded_file:
                            final_url = APIClient.upload_image(uploaded_file.getvalue(), uploaded_file.name, uploaded_file.type)
                            
                        if final_url:
                            res = APIClient.create_template_from_image(company_id, final_url, instructions)
                            if res and "id" in res:
                                st.success("Template created successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to process image or create template.")
                        else:
                            st.error("Failed to upload image.")

        with tab2:
            st.write("Generate a blank template from a description.")
            prompt = st.text_area("Template Description", placeholder="A clean minimalist design...", height=100)
            ratio = st.selectbox("Aspect Ratio", ["1:1", "3:4", "4:3", "9:16", "16:9"])
            
            if st.button("Generate Template", type="primary", key="gen_txt_tpl", width="stretch"):
                if not prompt:
                    st.error("Please provide a description.")
                else:
                    with st.spinner("Generating template..."):
                        res = APIClient.prompt_template(company_id, prompt, ratio)
                        if res and res.get("url"):
                            APIClient.create_template({
                                "company_id": company_id,
                                "template_url": res["url"],
                                "template_constraints": prompt,
                                "template_info": prompt[:50],
                                "aspect_ratio": ratio
                            })
                            st.success("Template generated successfully!")
                            st.rerun()

    st.divider()
    st.subheader("Your Templates")
    
    templates = APIClient.get_templates(company_id)
    if not templates:
        st.info("No templates found.")
        return
        
    cols = st.columns(3)
    for i, tpl in enumerate(templates):
        with cols[i % 3]:
            with st.container(border=True):
                if tpl.get("template_url"):
                    st.image(tpl["template_url"], width="stretch")
                else:
                    st.markdown("No Image")
                    
                st.caption(f"Ratio: {tpl.get('aspect_ratio', 'Unknown')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Edit", key=f"edit_{tpl['id']}", width="stretch"):
                        st.session_state.edit_template_id = tpl['id']
                        st.switch_page(st.session_state['pages_dict']['edit_template'])
                with col2:
                    if st.button("Delete", key=f"del_{tpl['id']}", width="stretch"):
                        APIClient.delete_template(tpl['id'])
                        st.rerun()

render()
