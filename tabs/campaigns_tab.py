import streamlit as st
import datetime
from services import db_services
from services.workflows import campaign_workflows


@st.dialog("Create Campaign")
def create_campaign_dialog(company_id):
    st.write("Campaign settings...")
    name = st.text_input("Campaign Name (Plan Title)")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    plan_brief = st.text_area("Campaign Plan / Brief (Used for AI Logic)")
    
    if st.button("Save", type="primary"):
        if not name:
            st.error("Please provide a campaign name.")
            return
            
        data = {
            "company_id": company_id,
            "plan_title": name,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "plan_content": plan_brief,
            "status": "active"
        }
        res = campaign_workflows.create_new_campaign(data)
        if res.get("success"):
            st.success(f"Campaign '{name}' created!")
            st.rerun()
        else:
            st.error(res.get("error"))


@st.dialog("Edit Campaign")
def edit_campaign_dialog(camp):
    st.subheader(f"Edit: {camp.get('plan_title')}")
    name = st.text_input("Campaign Name (Plan Title)", value=camp.get('plan_title', ''))
    
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
    
    plan_brief = st.text_area("Campaign Plan / Brief", value=camp.get('plan_content', ''))
    
    if st.button("Save Changes", type="primary"):
        if not name:
            st.error("Campaign name is required.")
            return
            
        update_data = {
            "plan_title": name,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "plan_content": plan_brief,
            "status": camp.get('status', 'active')
        }
        res = campaign_workflows.update_campaign_details(camp['id'], update_data)
        if res.get("success"):
            st.success("Campaign updated successfully!")
            st.rerun()
        else:
            st.error(res.get("error"))


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
    if st.button("Back to Campaigns", icon=":material/arrow_back:"):
        st.session_state.selected_campaign_id = None
        st.rerun()

    campaigns = db_services.get_campaigns(company_id)
    camp = next((c for c in campaigns if c['id'] == campaign_id), None)

    if not camp:
        st.error("Campaign not found.")
        st.session_state.selected_campaign_id = None
        return

    _render_campaign_header(camp)
    _render_ai_plan_section(campaign_id, company_id, camp)
    _render_generated_posts_section(campaign_id, company_id)


def _render_campaign_header(camp):
    """Renders the top header information of a campaign."""
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

    user_brief = camp.get('plan_content', '')
    if user_brief:
        with st.expander("Campaign Brief", icon=":material/description:"):
            st.write(user_brief)


def _render_ai_plan_section(campaign_id, company_id, camp):
    """Handles the display, generation, and editing of the AI Text Plan."""
    ai_plan_raw = camp.get('ai_plan')
    user_brief = camp.get('plan_content', '')

    st.subheader("AI Campaign Plan", divider="gray")
    if not ai_plan_raw:
        st.info("No AI plan has been generated for this campaign yet.")
        if st.button("Generate Campaign Plan", icon=":material/smart_toy:", type="primary"):
            _handle_generate_plan(campaign_id, company_id, camp, user_brief)
    else:
        st.success("AI Plan is ready!")
        with st.expander("Review and Edit AI Plan", expanded=True, icon=":material/edit_document:"):
            st.info("You can edit the text plan below. This exact text will be sent to the AI for the next step.")
            edited_plan_str = st.text_area("AI Plan (Text)", value=ai_plan_raw, height=300)
            
            if st.button("Save Edited AI Plan"):
                res = campaign_workflows.save_edited_campaign_plan(campaign_id, edited_plan_str)
                if res.get("success"):
                    st.success("Edited AI plan saved successfully!")
                    st.rerun()
                else:
                    st.error(res.get("error"))
        
        st.write("---")
        if st.button("Create Text", icon=":material/article:", type="primary", help="Generate daily text content based on the text plan"):
            _handle_create_text_action(campaign_id, company_id, camp, ai_plan_raw, user_brief)


def _handle_generate_plan(campaign_id, company_id, camp, user_brief):
    """Executes the AI task to generate the initial plain text plan."""
    with st.spinner("Generating campaign plan with AI..."):
        res = campaign_workflows.generate_and_save_ai_plan(campaign_id, company_id, camp, user_brief)
        if res.get("success"):
            st.success("Plan generated successfully!")
            st.rerun()
        else:
            st.error(res.get("error"))


def _handle_create_text_action(campaign_id, company_id, camp, ai_plan_raw, user_brief):
    """Loops over the campaign duration to generate detailed content for each day."""
    with st.spinner("Generating daily detailed text content..."):
        res = campaign_workflows.generate_daily_content_loop(campaign_id, company_id, camp, ai_plan_raw, user_brief)
        if res.get("success"):
            st.success("Text content generated successfully for all days! You can view them below or in Day Details.")
            st.rerun()
        else:
            st.error(res.get("error"))


def _render_generated_posts_section(campaign_id, company_id):
    """Renders the list of generated posts for the campaign."""
    all_content = db_services.get_scheduled_content(company_id)
    campaign_posts = [c for c in all_content if c.get('campaign_id') == campaign_id]

    if not campaign_posts:
        st.info("No text content is associated with this campaign yet. Click 'Create Text' to generate it.", icon=":material/info:")
        return

    st.subheader(f"Generated Posts ({len(campaign_posts)})", divider="gray")
    campaign_posts.sort(key=lambda x: x.get('publish_date', ''))

    for post in campaign_posts:
        with st.container(border=True):
            p_cols = st.columns([1, 3, 1])

            with p_cols[0]:
                images = post.get('post_images', [])
                if images and isinstance(images, list) and images:
                    st.image(images[0], width=100)
                else:
                    st.markdown(
                        "<div style='width:100px;height:75px;background:#1e293b;border-radius:8px;"
                        "display:flex;align-items:center;justify-content:center;color:#64748b;"
                        "font-size:11px;text-align:center;'>No image<br>(Generate in Details)</div>",
                        unsafe_allow_html=True
                    )

            with p_cols[1]:
                content_type = post.get('content_type', 'Post')
                publish_date = post.get('publish_date', 'N/A')
                publish_time = post.get('publish_time', 'N/A')

                st.markdown(f"**{content_type}** — {publish_date} at {publish_time}")

                h1 = post.get('h1', [])
                if h1 and isinstance(h1, list):
                    st.markdown(f"**{', '.join(h1)}**")

                caption = post.get('caption', '')
                if caption:
                    display_caption = caption[:120] + "..." if len(caption) > 120 else caption
                    st.caption(display_caption)

                st.badge(post.get('status', 'planned').capitalize(), icon=":material/circle:")

            with p_cols[2]:
                if st.button("View Details", key=f"view_post_{post['id']}", icon=":material/open_in_new:"):
                    try:
                        st.session_state.selected_date = datetime.date.fromisoformat(post.get('publish_date', ''))
                    except (ValueError, TypeError):
                        st.session_state.selected_date = datetime.date.today()
                    st.switch_page(st.session_state['pages_dict']['day_details'])
