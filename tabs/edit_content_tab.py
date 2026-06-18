import streamlit as st
import datetime
from services import db_services

def render():
    st.title("Edit Content")
    user = st.session_state.get('user', {})

    if user.get('role') == 'admin' and not user.get('company_id'):
        st.info("Admins must select a company first.", icon=":material/info:")
        if st.button("Go to Companies Dashboard", icon=":material/arrow_forward:"):
            st.switch_page(st.session_state['pages_dict']['admin_dashboard'])
        return

    # Check if we have a post to edit
    editing_post = st.session_state.get('editing_post')
    if not editing_post:
        st.warning("No post selected for editing.", icon=":material/warning:")
        st.caption("Navigate here by clicking 'Edit Details' on a post card.")
        if st.button("Go to Schedule", icon=":material/calendar_month:"):
            st.switch_page(st.session_state['pages_dict']['schedule'])
        return

    item = editing_post
    company_id = user.get('company_id')

    # Fetch campaigns for the dropdown
    campaigns = db_services.get_campaigns(company_id)
    campaign_map = {c['id']: c['plan_title'] for c in campaigns}
    campaign_ids = [None] + [c['id'] for c in campaigns]

    # Current campaign selection
    current_campaign_id = item.get('campaign_id')
    if current_campaign_id in campaign_ids:
        default_camp_idx = campaign_ids.index(current_campaign_id)
    else:
        default_camp_idx = 0

    # --- Text Editing Section ---
    st.subheader("Post Details", divider="gray")

    col_left, col_right = st.columns(2)

    with col_left:
        # H1 field - h1 is stored as an array
        h1_value = item.get('h1', [])
        if isinstance(h1_value, list):
            h1_str = ', '.join(h1_value) if h1_value else ''
        else:
            h1_str = str(h1_value) if h1_value else ''
        new_h1 = st.text_input("Title / H1", value=h1_str, key="edit_h1")

        # Caption
        caption_value = item.get('caption', '') or ''
        new_caption = st.text_area("Caption", value=caption_value, height=200, key="edit_caption")

    with col_right:
        # Content Type (display only)
        st.text_input("Content Type", value=item.get('content_type', 'N/A'), disabled=True)

        # Publish Date
        try:
            default_date = datetime.date.fromisoformat(item.get('publish_date', ''))
        except (ValueError, TypeError):
            default_date = datetime.date.today()
        new_date = st.date_input("Publish Date", value=default_date, key="edit_date")

        # Publish Time
        time_value = item.get('publish_time', '12:00:00') or '12:00:00'
        new_time = st.text_input("Publish Time (HH:MM)", value=time_value[:5], key="edit_time")

        # Campaign
        selected_campaign = st.selectbox(
            "Campaign",
            options=campaign_ids,
            index=default_camp_idx,
            format_func=lambda x: campaign_map.get(x, "No Campaign") if x else "No Campaign",
            key="edit_campaign"
        )

    # --- Image Editing Section ---
    st.subheader("Image Editor", divider="gray")

    current_images = item.get('post_images', []) or []

    if not current_images:
        st.caption("This post has no images.")
    else:
        st.caption(f"Current images ({len(current_images)}):")

        # Show current images in a row
        img_cols = st.columns(min(len(current_images), 4))
        for idx, img_url in enumerate(current_images):
            with img_cols[idx % 4]:
                st.image(img_url, width=150, caption=f"Image {idx + 1}")

    # Mock AI Image Modification
    st.markdown("**Modify image with AI**")
    st.caption("Enter a prompt describing the changes you want. The AI will generate a modified version.")

    if "edit_modified_image" not in st.session_state:
        st.session_state.edit_modified_image = None

    if "edit_mock_toggle" not in st.session_state:
        st.session_state.edit_mock_toggle = 0

    mod_prompt = st.text_input(
        "Image modification prompt",
        placeholder="e.g. Make the background darker, add a gradient overlay...",
        key="edit_img_prompt"
    )

    if st.button("Generate Modified Image", icon=":material/auto_fix_high:", type="secondary"):
        if not mod_prompt:
            st.error("Please enter a modification prompt.")
        else:
            with st.spinner("Generating modified image..."):
                import time
                time.sleep(1)  # Mock latency
                st.session_state.edit_mock_toggle = 1 - st.session_state.edit_mock_toggle
                mock_urls = [
                    "https://placehold.co/400x300/6366f1/ffffff?text=Modified+A",
                    "https://placehold.co/400x300/ec4899/ffffff?text=Modified+B"
                ]
                st.session_state.edit_modified_image = mock_urls[st.session_state.edit_mock_toggle]
                st.rerun()

    # Show comparison if we have a modified image
    if st.session_state.edit_modified_image:
        st.markdown("**Compare:**")
        comp_cols = st.columns(2)
        with comp_cols[0]:
            st.caption("Current Image")
            if current_images:
                st.image(current_images[0], width=250)
            else:
                st.info("No current image")
        with comp_cols[1]:
            st.caption("Modified Image (AI)")
            st.image(st.session_state.edit_modified_image, width=250)

        if st.button("Delete old image and save new one", icon=":material/swap_horiz:", type="primary"):
            # Replace the first image (or add if empty)
            new_images = [st.session_state.edit_modified_image]
            if len(current_images) > 1:
                new_images.extend(current_images[1:])

            update_result = db_services.update_content(item['id'], {"post_images": new_images})
            if update_result is not None:
                st.success("Image replaced successfully!")
                # Update local state
                st.session_state.editing_post['post_images'] = new_images
                st.session_state.edit_modified_image = None
                st.rerun()
            else:
                st.error("Failed to update the image.")

        if st.button("Cancel modification", icon=":material/close:"):
            st.session_state.edit_modified_image = None
            st.rerun()

    # --- Save & Navigation ---
    st.markdown("---")

    save_cols = st.columns([1, 1, 2])
    with save_cols[0]:
        if st.button("Save Changes", icon=":material/save:", type="primary"):
            # Parse H1 back to array
            h1_array = [h.strip() for h in new_h1.split(',') if h.strip()] if new_h1 else []

            # Format time
            formatted_time = new_time
            if len(new_time) == 5:
                formatted_time = new_time + ":00"

            update_data = {
                "h1": h1_array,
                "caption": new_caption,
                "publish_date": str(new_date),
                "publish_time": formatted_time,
                "campaign_id": selected_campaign,
            }

            result = db_services.update_content(item['id'], update_data)
            if result is not None:
                st.success("Content updated successfully!")
                # Update session state
                st.session_state.editing_post.update(update_data)
                # Navigate back to day details
                st.session_state.selected_date = new_date
                import time
                time.sleep(0.5)
                st.switch_page(st.session_state['pages_dict']['day_details'])
            else:
                st.error("Failed to save changes.")

    with save_cols[1]:
        if st.button("Back to Day Details", icon=":material/arrow_back:"):
            st.session_state.edit_modified_image = None
            st.switch_page(st.session_state['pages_dict']['day_details'])
