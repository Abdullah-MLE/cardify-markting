"""Shared UI guard components."""
import streamlit as st


def require_company() -> int | None:
    """
    Guard: returns company_id if selected, else shows info + redirect button and returns None.
    Usage: company_id = require_company(); if not company_id: return
    """
    user = st.session_state.get("user", {})
    company_id = user.get("company_id")

    if not company_id:
        if user.get("role") == "admin":
            st.info("Admins must select a company first.", icon=":material/info:")
            if st.button("Go to Companies Dashboard", icon=":material/arrow_forward:"):
                st.switch_page(st.session_state["pages_dict"]["admin_dashboard"])
        else:
            st.warning("No company selected.", icon=":material/warning:")
        return None

    return company_id


def get_user() -> dict:
    """Return the current user dict from session state."""
    return st.session_state.get("user", {})
