"""Campaigns Page."""
import streamlit as st
from frontend.api_client import APIClient
from frontend.components.guards import require_company
from frontend.components.content_card import render_mini_card
from frontend.dialogs.campaign_dialogs import create_campaign_dialog, edit_campaign_dialog

def render():
    st.title("Campaigns")
    
    company_id = require_company()
    if not company_id:
        return
        
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write("Manage your marketing campaigns and weekly plans.")
    with col2:
        if st.button("New Campaign", icon=":material/add:", type="primary", width="stretch"):
            create_campaign_dialog(company_id)
            
    campaigns = APIClient.get_campaigns(company_id)
    
    if not campaigns:
        st.info("No campaigns found. Create one to get started.", icon=":material/info:")
        return
        
    for camp in sorted(campaigns, key=lambda x: x.get('start_date', ''), reverse=True):
        render_campaign_row(camp, company_id)

def render_campaign_row(camp: dict, company_id: int):
    """Render a single campaign row in an expander."""
    status_color = "green" if camp.get("status") == "active" else "gray"
    
    with st.expander(f"📅 {camp['plan_title']} ({camp.get('start_date')} to {camp.get('end_date')})"):
        # Header actions
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**Status:** :{status_color}[{camp.get('status', 'draft').upper()}]")
        with col2:
            if st.button("Edit Details", key=f"edit_camp_{camp['id']}", icon=":material/edit:"):
                edit_campaign_dialog(camp)
                
        st.divider()
        
        # Tabs for Plan and Content
        tab1, tab2 = st.tabs(["AI Plan", "Content Items"])
        
        with tab1:
            render_campaign_plan_tab(camp, company_id)
            
        with tab2:
            render_campaign_content_tab(camp, company_id)

def render_campaign_plan_tab(camp: dict, company_id: int):
    """Render the AI Plan generation and editing tab."""
    ai_plan = camp.get('ai_plan')
    
    if not ai_plan:
        st.info("No AI Plan generated yet.")
        with st.form(f"gen_plan_form_{camp['id']}"):
            user_brief = st.text_area("Manager Notes / Goal", placeholder="Focus on our new summer collection...")
            if st.form_submit_button("Generate AI Plan", type="primary"):
                with st.spinner("Generating AI Plan..."):
                    plan_text = APIClient.generate_ai_plan(camp['id'], company_id, camp, user_brief)
                    if plan_text:
                        APIClient.update_campaign(camp['id'], {"ai_plan": plan_text})
                        st.success("Plan generated!")
                        st.rerun()
    else:
        # Edit existing plan
        with st.form(f"edit_plan_form_{camp['id']}"):
            edited_plan = st.text_area("AI Plan (Editable)", value=ai_plan, height=300)
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Changes"):
                    APIClient.update_campaign(camp['id'], {"ai_plan": edited_plan})
                    st.success("Saved!")
                    st.rerun()
            with col2:
                # Option to regenerate daily content based on plan
                if st.form_submit_button("Generate Daily Posts from Plan", type="primary"):
                    st.session_state[f"show_gen_posts_form_{camp['id']}"] = True
                    st.rerun()
                    
        # Confirm Generation
        if st.session_state.get(f"show_gen_posts_form_{camp['id']}", False):
            with st.container(border=True):
                st.warning("This will generate detailed post content for each day in the campaign. Proceed?")
                user_brief = st.text_input("Additional Notes for Content Generator", key=f"brief_gen_{camp['id']}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Cancel", key=f"cancel_gen_{camp['id']}"):
                        st.session_state[f"show_gen_posts_form_{camp['id']}"] = False
                        st.rerun()
                with c2:
                    if st.button("Confirm & Generate", type="primary", key=f"confirm_gen_{camp['id']}"):
                        with st.spinner("Generating content... This may take a minute."):
                            res = APIClient.generate_campaign_content(
                                camp['id'], company_id, camp, ai_plan, user_brief
                            )
                            if res and res.get("success"):
                                st.success("Daily content generated!")
                                st.session_state[f"show_gen_posts_form_{camp['id']}"] = False
                                st.rerun()

def render_campaign_content_tab(camp: dict, company_id: int):
    """Render the list of content items under this campaign."""
    all_content = APIClient.get_scheduled_content(company_id)
    camp_content = [c for c in all_content if c.get('campaign_id') == camp['id']]
    
    if not camp_content:
        st.info("No content generated yet. Go to AI Plan to generate daily posts.")
        return
        
    # Stats
    with st.container(border=True):
        st.markdown("#### Campaign Stats")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", len(camp_content))
        with col2:
            with_img = sum(1 for c in camp_content if c.get('post_images'))
            st.metric("With Images", with_img)
        with col3:
            st.metric("Without Images", len(camp_content) - with_img)
            
        if with_img < len(camp_content):
            if st.button("Auto-Generate Missing Images", key=f"auto_img_{camp['id']}"):
                st.info("Bulk image generation feature coming soon.")
                
    st.divider()
    
    # Sort content by date
    camp_content.sort(key=lambda x: (x.get('publish_date', ''), x.get('publish_time', '')))
    
    for item in camp_content:
        render_mini_card(item, on_view_key_suffix=f"camp_{camp['id']}")

render()
