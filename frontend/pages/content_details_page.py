"""Content Details Page."""
import streamlit as st
from frontend.api_client import APIClient
from frontend.components.guards import require_company
from frontend.components.image_placeholder import render_image_placeholder

def render():
    company_id = require_company()
    if not company_id:
        return
        
    content_id = st.session_state.get('selected_content_id')
    if not content_id:
        st.error("No content selected.")
        if st.button("Go to Schedule"):
            st.switch_page(st.session_state['pages_dict']['schedule'])
        return

    # Fetch latest data
    all_content = APIClient.get_scheduled_content(company_id)
    item_matches = [c for c in all_content if c['id'] == content_id]
    if not item_matches:
        st.error("Content not found in database.")
        return
        
    item = item_matches[0]
    ctype = item.get('content_type', 'post')
    
    st.title(f"{ctype.capitalize()} Details")
    
    # Navigation and Delete
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.button("← Back"):
            st.switch_page(st.session_state['pages_dict']['schedule'])
    with col2:
        if st.button("Delete Post", type="primary", icon=":material/delete:"):
            APIClient.delete_content(content_id)
            st.success("Deleted!")
            st.switch_page(st.session_state['pages_dict']['schedule'])

    st.divider()
    
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.subheader("Text Content")
        with st.container(border=True):
            st.markdown(f"**Status:** {item.get('status', 'planned')}")
            st.markdown(f"**Date:** {item.get('publish_date')} at {item.get('publish_time')}")
            
            st.divider()
            
            headlines = item.get('h1', [])
            if not isinstance(headlines, list):
                headlines = [headlines]
                
            post_ideas = item.get('post_idea', [])
            if not isinstance(post_ideas, list):
                post_ideas = [post_ideas]
                
            if ctype == 'carousel':
                for i, (h, idea) in enumerate(zip(headlines, post_ideas)):
                    st.markdown(f"**Slide {i+1} Headline:** {h}")
                    st.caption(f"Visual: {idea}")
            else:
                st.markdown(f"**Headline:** {headlines[0] if headlines else ''}")
                st.caption(f"Visual: {post_ideas[0] if post_ideas else ''}")
                
            st.divider()
            st.markdown("**Caption:**")
            st.write(item.get('caption', ''))
            
        with st.expander("Edit Text"):
            with st.form("edit_text_form"):
                new_status = st.selectbox("Status", ["planned", "published"], index=0 if item.get('status') == 'planned' else 1)
                new_caption = st.text_area("Caption", value=item.get('caption', ''))
                if st.form_submit_button("Save Changes"):
                    APIClient.update_content(content_id, {"status": new_status, "caption": new_caption})
                    st.success("Saved!")
                    st.rerun()

    with right_col:
        st.subheader("Media")
        images = item.get('post_images', [])
        
        templates = APIClient.get_templates(company_id)
        template_options = {t['id']: t.get('template_info', f"Template {t['id']}") for t in templates}
        template_options[None] = "No Template (AI Direct)"
        
        selected_template_id = st.selectbox(
            "Select Template for Generation", 
            options=list(template_options.keys()), 
            format_func=lambda x: template_options[x]
        )
        
        user_instructions = st.text_input("Additional Image Instructions (Optional)")
        
        if st.button("Generate Image(s)", type="primary", width="stretch"):
            with st.spinner("Generating media..."):
                urls = APIClient.generate_media(content_id, selected_template_id, user_instructions)
                if urls:
                    APIClient.update_content(content_id, {"post_images": urls})
                    st.success("Images generated!")
                    st.rerun()
                    
        st.divider()
        
        if not images:
            render_image_placeholder()
        else:
            if ctype == 'carousel':
                tabs = st.tabs([f"Slide {i+1}" for i in range(len(images))])
                for i, (tab, img_url) in enumerate(zip(tabs, images)):
                    with tab:
                        if img_url:
                            st.image(img_url, width="stretch")
                            with st.expander("Edit this slide"):
                                notes = st.text_input("Edit Instructions", key=f"edit_inp_{i}")
                                if st.button("Apply Edit", key=f"edit_btn_{i}"):
                                    with st.spinner("Editing..."):
                                        new_url = APIClient.edit_media(content_id, notes, slide_index=i)
                                        if new_url:
                                            images[i] = new_url
                                            APIClient.update_content(content_id, {"post_images": images})
                                            st.rerun()
                        else:
                            render_image_placeholder()
            else:
                img_url = images[0]
                if img_url:
                    st.image(img_url, width="stretch")
                    with st.expander("Edit Image"):
                        notes = st.text_input("Edit Instructions")
                        if st.button("Apply Edit"):
                            with st.spinner("Editing..."):
                                new_url = APIClient.edit_media(content_id, notes)
                                if new_url:
                                    APIClient.update_content(content_id, {"post_images": [new_url]})
                                    st.rerun()
                else:
                    render_image_placeholder()

render()
