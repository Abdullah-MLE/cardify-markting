import streamlit as st
import datetime
from services import db_services


@st.dialog("Create Campaign")
def create_campaign_dialog(company_id):
    st.write("Campaign settings...")
    name = st.text_input("Campaign Name (Plan Title)")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    plan_content = st.text_area("Campaign Plan / Brief (Used for AI Logic)")
    
    if st.button("Save", type="primary"):
        if not name:
            st.error("Please provide a campaign name.")
            return
            
        data = {
            "company_id": company_id,
            "plan_title": name,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "plan_content": plan_content,
            "status": "active"
        }
        res = db_services.create_campaign(data)
        if res:
            st.success(f"Campaign '{name}' created!")
            st.rerun()
        else:
            st.error("Failed to create campaign.")

@st.dialog("Edit Campaign")
def edit_campaign_dialog(camp):
    st.subheader(f"Edit: {camp.get('plan_title')}")
    name = st.text_input("Campaign Name (Plan Title)", value=camp.get('plan_title', ''))
    
    # parse dates
    try:
        sd = datetime.date.fromisoformat(camp.get('start_date', ''))
    except (ValueError, TypeError):
        sd = datetime.date.today()
    try:
        ed = datetime.date.fromisoformat(camp.get('end_date', ''))
    except (ValueError, TypeError):
        ed = datetime.date.today()
        
    start_date = st.date_input("Start Date", value=sd)
    end_date = st.date_input("End Date", value=ed)
    plan_content = st.text_area("Campaign Plan / Brief", value=camp.get('plan_content', ''))
    
    current_status = camp.get('status', 'draft')
    status_options = ["draft", "active", "completed"]
    status_idx = status_options.index(current_status) if current_status in status_options else 0
    status = st.selectbox("Status", status_options, index=status_idx)
    
    if st.button("Save Changes", type="primary"):
        if not name:
            st.error("Campaign name is required.")
            return
            
        update_data = {
            "plan_title": name,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "plan_content": plan_content,
            "status": status
        }
        res = db_services.update_campaign(camp['id'], update_data)
        if res is not None:
            st.success("Campaign updated successfully!")
            st.rerun()
        else:
            st.error("Failed to update campaign.")


def render():
    st.title("Campaigns")
    user = st.session_state.get('user', {})
    
    if user.get('role') == 'admin' and not user.get('company_id'):
        st.info("Admins must select a company to view campaigns.", icon=":material/info:")
        if st.button("Go to Companies Dashboard", icon=":material/arrow_forward:"):
            st.switch_page(st.session_state['pages_dict']['admin_dashboard'])
        return

    company_id = user.get('company_id')

    # Check if we are in "Campaign Details" view
    selected_campaign_id = st.session_state.get('selected_campaign_id')

    if selected_campaign_id:
        _render_campaign_details(selected_campaign_id, company_id)
        return

    # ─── Campaign List View ────────────────────────────────────────
    with st.container():
        if st.button("New Campaign", icon=":material/add:", type="primary"):
            create_campaign_dialog(company_id)
            
    campaigns = db_services.get_campaigns(company_id)
    
    if not campaigns:
        st.info("No campaigns found. Create your first campaign!", icon=":material/info:")
        return
        
    for camp in campaigns:
        with st.container(border=True):
            cols = st.columns([3, 1])
            with cols[0]:
                st.subheader(camp.get('plan_title', 'Unnamed'))
                st.caption(f"Duration: {camp.get('start_date')} to {camp.get('end_date')}")
                brief = camp.get('plan_content', '')
                if brief:
                    # Truncate long briefs
                    display_brief = brief[:200] + "..." if len(brief) > 200 else brief
                    st.markdown(f"**Brief:** {display_brief}")
            with cols[1]:
                status = camp.get('status', 'draft')
                color_map = {"active": "green", "completed": "blue", "draft": "gray"}
                st.badge(status.capitalize(), icon=":material/circle:", color=color_map.get(status, "gray"))
                
                st.write("")  # padding
                if st.button("View Details", key=f"view_camp_{camp['id']}", icon=":material/visibility:", type="secondary"):
                    st.session_state.selected_campaign_id = camp['id']
                    st.rerun()
                if st.button("Edit", key=f"edit_camp_{camp['id']}", icon=":material/edit:"):
                    edit_campaign_dialog(camp)
                if st.button("Delete", key=f"delete_camp_{camp['id']}", icon=":material/delete:"):
                    if db_services.delete_campaign(camp['id']):
                        st.success("Deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete campaign.")


def _render_campaign_details(campaign_id, company_id):
    """Render the Campaign Details sub-view showing all posts for a campaign."""

    # Back button
    if st.button("Back to Campaigns", icon=":material/arrow_back:"):
        st.session_state.selected_campaign_id = None
        st.rerun()

    # Find the campaign
    campaigns = db_services.get_campaigns(company_id)
    camp = None
    for c in campaigns:
        if c['id'] == campaign_id:
            camp = c
            break

    if not camp:
        st.error("Campaign not found.")
        st.session_state.selected_campaign_id = None
        return

    # Campaign header
    st.subheader(camp.get('plan_title', 'Unnamed Campaign'))

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        status = camp.get('status', 'draft')
        color_map = {"active": "green", "completed": "blue", "draft": "gray"}
        st.badge(status.capitalize(), icon=":material/circle:", color=color_map.get(status, "gray"))
    with col_info2:
        st.caption(f":material/date_range: {camp.get('start_date')} → {camp.get('end_date')}")
    with col_info3:
        st.caption(f":material/business: Company ID: {camp.get('company_id')}")

    if camp.get('plan_content'):
        with st.expander("Campaign Brief", icon=":material/description:"):
            st.write(camp['plan_content'])

    # Fetch posts for this campaign
    all_content = db_services.get_scheduled_content(company_id)
    campaign_posts = [c for c in all_content if c.get('campaign_id') == campaign_id]

    if not campaign_posts:
        st.info("No posts are associated with this campaign yet.", icon=":material/info:")
        return

    st.subheader(f"Posts ({len(campaign_posts)})", divider="gray")

    # Sort by publish_date
    campaign_posts.sort(key=lambda x: x.get('publish_date', ''))

    for post in campaign_posts:
        with st.container(border=True):
            p_cols = st.columns([1, 3, 1])

            with p_cols[0]:
                # Show thumbnail
                images = post.get('post_images', [])
                if images and isinstance(images, list) and images:
                    st.image(images[0], width=100)
                else:
                    st.markdown(
                        "<div style='width:100px;height:75px;background:#1e293b;border-radius:8px;"
                        "display:flex;align-items:center;justify-content:center;color:#64748b;"
                        "font-size:11px;'>No image</div>",
                        unsafe_allow_html=True
                    )

            with p_cols[1]:
                content_type = post.get('content_type', 'Post')
                publish_date = post.get('publish_date', 'N/A')
                publish_time = post.get('publish_time', 'N/A')

                st.markdown(f"**{content_type}** — {publish_date} at {publish_time}")

                # H1
                h1 = post.get('h1', [])
                if h1 and isinstance(h1, list):
                    st.markdown(f"**{', '.join(h1)}**")

                # Caption (truncated)
                caption = post.get('caption', '')
                if caption:
                    display_caption = caption[:120] + "..." if len(caption) > 120 else caption
                    st.caption(display_caption)

                # Status badge
                post_status = post.get('status', 'planned')
                st.badge(post_status.capitalize(), icon=":material/circle:")

            with p_cols[2]:
                if st.button("View", key=f"view_post_{post['id']}", icon=":material/open_in_new:"):
                    # Navigate to day details for that date
                    try:
                        st.session_state.selected_date = datetime.date.fromisoformat(post.get('publish_date', ''))
                    except (ValueError, TypeError):
                        st.session_state.selected_date = datetime.date.today()
                    st.switch_page(st.session_state['pages_dict']['day_details'])
