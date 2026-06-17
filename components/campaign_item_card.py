import streamlit as st
from services import db_services


def render_item_card(item, campaigns=None):
    with st.container(border=True):
        # --- Header: content type and time ---
        content_type = item.get('content_type', 'Post')
        publish_time = item.get('publish_time') or 'N/A'
        st.write(f"### 📝 {content_type.capitalize()} — {publish_time}")

        # --- Campaign name lookup ---
        campaign_id = item.get('campaign_id')
        campaign_name = None
        if campaign_id and campaigns:
            for c in campaigns:
                if c.get('id') == campaign_id:
                    campaign_name = c.get('plan_title')
                    break
        if campaign_name:
            st.caption(f"📋 Campaign: **{campaign_name}**")

        # --- Status badge ---
        status = item.get('status', 'draft')
        status_colors = {
            'published': '🟢',
            'scheduled': '🔵',
            'draft': '⚪',
            'failed': '🔴',
        }
        status_icon = status_colors.get(status, '⚪')
        st.write(f"{status_icon} Status: **{status.capitalize()}**")

        # --- H1 headline (array, join with ', ') ---
        h1 = item.get('h1')
        if h1 and isinstance(h1, list):
            headline_text = ', '.join(str(h) for h in h1 if h)
            if headline_text:
                st.write(f"**Headline:** {headline_text}")

        # --- Caption (truncated to 150 chars) ---
        caption_text = item.get('caption') or ''
        if caption_text:
            display_caption = caption_text[:150] + '...' if len(caption_text) > 150 else caption_text
            st.write(f"**Caption:** {display_caption}")

        # --- Image preview: small thumbnails, max 4 ---
        images = item.get('post_images')
        if images and isinstance(images, list):
            preview_images = images[:4]
            img_cols = st.columns(len(preview_images))
            for idx, img_url in enumerate(preview_images):
                with img_cols[idx]:
                    st.image(img_url, width=100)

        # --- Action buttons ---
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("Edit Details", key=f"edit_btn_{item.get('id')}", icon=":material/edit:"):
                st.session_state.editing_post = item
                st.switch_page(st.session_state['pages_dict']['edit_content'])
        with btn_col2:
            if st.button("Delete Content", key=f"delete_btn_{item.get('id')}", icon=":material/delete:"):
                if db_services.delete_content(item['id']):
                    st.success("Deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete.")
