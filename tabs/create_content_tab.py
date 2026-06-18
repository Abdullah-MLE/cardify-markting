import streamlit as st
import datetime
import time
from services import db_services
from services.ai_service import get_ai_service
from schemas.ai_models import SinglePostGeneration


def render():
    st.title("Create Content")
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

    # Initialize creation state
    st.session_state.setdefault('create_mode', None)          # 'manual' or 'ai'
    st.session_state.setdefault('create_content_type', None)  # 'text', 'text_image', 'carousel'
    st.session_state.setdefault('create_ai_result', None)
    st.session_state.setdefault('create_carousel_slides', [])
    st.session_state.setdefault('create_generated_image', None)

    # ─── Step 1: Choose AI or Manual ───────────────────────────────
    if st.session_state.create_mode is None:
      
        if not gen_prompt:
            st.error("Please enter a prompt.")
        else:
            with st.spinner("Generating image with AI..."):
                ai = get_ai_service()
                context = {
                    "prompt": gen_prompt,
                    "headline": "",
                    "post_idea": gen_prompt,
                    "template_constraints": "",
                }
                if selected_template:
                    tpl = next((t for t in templates if t['id'] == selected_template), None)
                    if tpl:
                        context["template_constraints"] = tpl.get('template_constraints', '')

                media = [template_url] if template_url else None
                result = ai.execute_image_skill(
                    "generate_image",
                    context=context,
                    media=media,
                    aspect_ratio=aspect_ratio,
                )

                if result.get("success"):
                    with st.spinner("Uploading to storage..."):
                        img_url = db_services.upload_image(result["content"])
                        if img_url:
                            st.session_state.create_generated_image = img_url
                        else:
                            st.error("Generated image, but failed to upload to storage.")
                    st.rerun()
                else:
                    st.error(f"Image generation failed: {result.get('error', 'Unknown error')}")

    if st.session_state.create_generated_image:
        st.image(st.session_state.create_generated_image, width=300, caption="Generated preview")
        return [st.session_state.create_generated_image]

    return []
