import streamlit as st
import io
from services import db_services

def render():
    st.title("Image Generation")
    user = st.session_state.get('user', {})
    
    if user.get('role') == 'admin' and not user.get('company_id'):
        st.info("Admins must select a company to generate images.", icon=":material/info:")
        if st.button("Go to Companies Dashboard", icon=":material/arrow_forward:"):
            st.switch_page(st.session_state['pages_dict']['admin_dashboard'])
        return

    company_id = user.get('company_id')

    # Template selection
    templates = db_services.get_templates(company_id)
    selected_template = None
    template_url = None
    aspect_ratio = "1:1"

    if templates:
        template_options = {None: "No Template"}
        template_options.update({t['id']: t.get('template_info', 'Unnamed') for t in templates})
        selected_template = st.selectbox(
            "Select a Template (optional)",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x],
            key="img_gen_template"
        )
        if selected_template:
            tpl = next((t for t in templates if t['id'] == selected_template), None)
            if tpl:
                col_preview, col_info = st.columns([1, 2])
                with col_preview:
                    tpl_url = tpl.get('template_url')
                    if tpl_url:
                        st.image(tpl_url, width=150, caption="Template Preview")
                    else:
                        st.markdown(
                            "<div style='width:150px;height:112px;background:#1e293b;border-radius:8px;"
                            "display:flex;align-items:center;justify-content:center;color:#64748b;"
                            "font-size:11px;border: 1px solid #334155;'>No preview image</div>",
                            unsafe_allow_html=True
                        )
                with col_info:
                    st.markdown(f"**Aspect Ratio:** `{tpl.get('aspect_ratio', 'N/A')}`")
                    constraints = tpl.get('template_constraints')
                    if constraints:
                        st.markdown(f"**Constraints:**\n{constraints}")
                template_url = tpl.get('template_url')
                aspect_ratio = tpl.get('aspect_ratio', '1:1')
    else:
        st.caption("No templates available. You can create templates in the Templates page.")

    prompt = st.text_area(
        "Describe the image you want to generate",
        placeholder="e.g. A modern social media post with gradient background featuring..."
    )
    
    if "generated_image" not in st.session_state:
        st.session_state.generated_image = None

    if st.button("Generate Image", icon=":material/brush:", type="primary"):
        if not prompt:
            st.error("Please enter a prompt.")
        else:
            with st.spinner("Generating image with AI..."):
                from services.workflows import content_workflows
                
                tpl = None
                if selected_template:
                    tpl = next((t for t in templates if t['id'] == selected_template), None)
                
                res = content_workflows.generate_standalone_image(prompt, company_id, tpl)

                if res.get("success"):
                    st.session_state.generated_image = {
                        "bytes": res["data"],
                        "prompt": prompt
                    }
                else:
                    st.error(f"Image generation failed: {res.get('error', 'Unknown error')}")

    if st.session_state.generated_image:
        st.subheader("Generated Result", divider="gray")
        image_data = st.session_state.generated_image
        st.image(image_data["bytes"], width=400, caption=f"Prompt: {image_data['prompt']}")
        
        # Save to DB form
        with st.form("save_image_form"):
            st.write("Save this image as content in the database:")
            publish_date = st.date_input("Publish Date")
            
            campaigns = db_services.get_campaigns(company_id)
            campaign_options = {c['id']: c['plan_title'] for c in campaigns}
            campaign_options[None] = "No Campaign"
            
            selected_campaign = st.selectbox("Associate with Campaign", options=list(campaign_options.keys()), format_func=lambda x: campaign_options[x])
            
            if st.form_submit_button("Save to Database", type="primary"):
                with st.spinner("Uploading to storage..."):
                    img_url = db_services.upload_image(image_data["bytes"])
                    if not img_url:
                        st.error("Failed to upload image.")
                        return
                        
                content_data = {
                    "company_id": company_id,
                    "campaign_id": selected_campaign,
                    "content_type": "image",
                    "publish_date": str(publish_date),
                    "caption": image_data["prompt"],
                    "post_images": [img_url],
                    "status": "planned"
                }
                res = db_services.create_content(content_data)
                if res:
                    st.success("Successfully saved to database!")
                    st.session_state.generated_image = None
                    st.rerun()
                else:
                    st.error("Failed to save to database.")
