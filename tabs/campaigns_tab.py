import streamlit as st
import datetime
import json
from services import db_services
from services.ai_service import get_ai_service
from schemas.ai_models import WeeklyPlanGeneration, DayContentGeneration


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

    # AI Plan handling
    # ai_plan is assumed to be stored in the 'ai_plan' DB column as a JSON string or dict
    ai_plan_raw = camp.get('ai_plan')
    ai_plan = None
    if ai_plan_raw:
        if isinstance(ai_plan_raw, str):
            try:
                ai_plan = json.loads(ai_plan_raw)
            except:
                ai_plan = None
        else:
            ai_plan = ai_plan_raw

    st.subheader("AI Campaign Plan", divider="gray")
    if not ai_plan:
        st.info("No AI plan has been generated for this campaign yet.")
        if st.button("Generate Campaign Plan", icon=":material/smart_toy:", type="primary"):
            with st.spinner("Generating campaign plan with AI..."):
                ai = get_ai_service()
                company_data = db_services.get_company_data(company_id) or {}
                
                context = {
                    "company": company_data,
                    "campaign": camp,
                    "start_date": camp.get('start_date', ''),
                    "notes": user_brief
                }
                result = ai.execute_text_skill("create_weekly_plan", context, response_schema=WeeklyPlanGeneration)
                
                if result.get("success"):
                    generated_plan = result["content"]
                    # Save back to DB column `ai_plan`
                    # Supabase accepts either stringified JSON or dict if it's JSONB.
                    # We'll use json dumps for safety if it's a Text column.
                    plan_dict = generated_plan.model_dump() if hasattr(generated_plan, 'model_dump') else generated_plan.dict() if hasattr(generated_plan, 'dict') else generated_plan
                    update_data = {
                        "ai_plan": json.dumps(plan_dict, ensure_ascii=False)
                    }
                    db_services.update_campaign(campaign_id, update_data)
                    st.success("Plan generated successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to generate plan: {result.get('error')}")
    else:
        # Display editable AI Plan
        st.success("AI Plan is ready!")
        with st.expander("Review and Edit AI Plan", expanded=True, icon=":material/edit_document:"):
            st.info("You can edit the JSON below to tweak the plan before creating the text for each day.")
            
            # Format the JSON nicely for the text area
            formatted_json = json.dumps(ai_plan, indent=4, ensure_ascii=False)
            
            edited_json_str = st.text_area("AI Plan (JSON)", value=formatted_json, height=300)
            
            if st.button("Save Edited AI Plan"):
                try:
                    # Validate JSON
                    parsed_edited = json.loads(edited_json_str)
                    update_data = {
                        "ai_plan": json.dumps(parsed_edited, ensure_ascii=False)
                    }
                    res = db_services.update_campaign(campaign_id, update_data)
                    if res is not None:
                        st.success("Edited AI plan saved successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to save changes to the DB.")
                except json.JSONDecodeError:
                    st.error("Invalid JSON. Please check the formatting before saving.")
        
        st.write("---")
        # Text Generation button
        if st.button("Create Text", icon=":material/article:", type="primary", help="Generate daily text content (without images) based on the AI plan"):
            with st.spinner("Generating daily detailed text content..."):
                ai = get_ai_service()
                company_data = db_services.get_company_data(company_id) or {}
                
                try:
                    start_dt = datetime.date.fromisoformat(camp.get('start_date', ''))
                except:
                    start_dt = datetime.date.today()

                all_success = True
                days = ai_plan.get('days', [])
                for idx, day in enumerate(days):
                    current_dt = start_dt + datetime.timedelta(days=idx)
                    
                    context = {
                        "weekly_plan": ai_plan,
                        "company": company_data,
                        "date": str(current_dt),
                        "day_name": day.get('day_name', ''),
                        "day_order": str(idx + 1),
                        "notes": user_brief
                    }
                    
                    res = ai.execute_text_skill("generate_day_content", context, response_schema=DayContentGeneration)
                    if res.get("success"):
                        day_content_obj = res.get("content", {})
                        day_content = day_content_obj.model_dump() if hasattr(day_content_obj, 'model_dump') else day_content_obj.dict() if hasattr(day_content_obj, 'dict') else day_content_obj
                        items = day_content.get("content_list", [])
                        for item in items:
                            db_item = {
                                "company_id": company_id,
                                "campaign_id": campaign_id,
                                "content_type": item.get("type", "post"),
                                "publish_date": str(current_dt),
                                "publish_time": f"{item.get('posting_hour', 12):02d}:00:00",
                                "status": "planned",
                                "h1": item.get("headlines", []),
                                "caption": item.get("caption", ""),
                                "post_images": [],  # INTENTIONALLY EMPTY (no images generated yet)
                                "publish_day": current_dt.strftime("%A"),
                                "use_character": False,
                                "post_idea": "\n".join(item.get("post_ideas", []))
                            }
                            db_services.create_content(db_item)
                    else:
                        st.error(f"Failed generating content for {current_dt}: {res.get('error')}")
                        all_success = False

                if all_success:
                    st.success("Text content generated successfully for all days! You can view them below or in Day Details.")
                    st.rerun()

    # Fetch posts for this campaign
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
