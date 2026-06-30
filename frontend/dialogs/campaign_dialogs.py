"""Campaign dialogs."""
import streamlit as st
import datetime
from frontend.api_client import APIClient


@st.dialog("Create Campaign")
def create_campaign_dialog(company_id: int):
    st.subheader("Add a new campaign")
    title = st.text_input("Campaign Title")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.date.today())
    with col2:
        end_date = st.date_input("End Date", value=datetime.date.today() + datetime.timedelta(days=7))

    if st.button("Save", type="primary"):
        if title:
            data = {
                "company_id": company_id,
                "plan_title": title,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "status": "draft",
            }
            if APIClient.create_campaign(data):
                st.success("Campaign created!")
                st.rerun()
            else:
                st.error("Failed to create campaign.")
        else:
            st.error("Title is required.")


@st.dialog("Edit Campaign")
def edit_campaign_dialog(campaign: dict):
    st.subheader("Edit Campaign")
    title = st.text_input("Title", value=campaign.get("plan_title", ""))

    try:
        sd = datetime.date.fromisoformat(campaign.get("start_date", ""))
    except Exception:
        sd = datetime.date.today()

    try:
        ed = datetime.date.fromisoformat(campaign.get("end_date", ""))
    except Exception:
        ed = datetime.date.today() + datetime.timedelta(days=7)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=sd)
    with col2:
        end_date = st.date_input("End Date", value=ed)

    if st.button("Update", type="primary"):
        if title:
            data = {
                "plan_title": title,
                "start_date": str(start_date),
                "end_date": str(end_date),
            }
            if APIClient.update_campaign(campaign["id"], data):
                st.success("Updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update.")
        else:
            st.error("Title is required.")
