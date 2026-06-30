"""Company management dialogs."""
import streamlit as st
from frontend.api_client import APIClient


@st.dialog("Add New Company")
def add_company_dialog():
    st.subheader("Create a new company")
    name = st.text_input("Company Name")
    industry = st.text_input("Industry")

    if st.button("Save", type="primary"):
        if name:
            new_comp = {"company_name": name, "industry": industry}
            if APIClient.create_company(new_comp):
                st.success(f"Company '{name}' added successfully!")
                st.rerun()
            else:
                st.error("Database error.")
        else:
            st.error("Company name is required.")


@st.dialog("Edit Company")
def edit_company_dialog(company_id: int):
    comp = APIClient.get_company(company_id)
    if not comp:
        st.error("Company not found.")
        return

    st.subheader(f"Edit {comp.get('company_name')}")
    name = st.text_input("Company Name", value=comp.get("company_name", ""))
    industry = st.text_input("Industry", value=comp.get("industry", ""))

    if st.button("Update", type="primary"):
        if name:
            if APIClient.update_company(company_id, {"company_name": name, "industry": industry}):
                st.success("Updated successfully!")
                st.rerun()
            else:
                st.error("Database error.")
        else:
            st.error("Company name is required.")


@st.dialog("Delete Company")
def delete_company_dialog(company_id: int):
    comp = APIClient.get_company(company_id)
    if not comp:
        st.error("Company not found.")
        return

    st.warning(f"Are you sure you want to delete '{comp.get('company_name')}'?")
    st.markdown("**Warning:** This will delete all associated campaigns, content, and templates.")

    if st.button("Yes, Delete Completely", type="primary"):
        if APIClient.delete_company(company_id):
            st.success("Deleted successfully.")
            st.session_state.pop("user_company_id", None)
            if st.session_state.get("user", {}).get("company_id") == company_id:
                st.session_state["user"]["company_id"] = None
            st.rerun()
        else:
            st.error("Failed to delete company.")


@st.dialog("Manage Users")
def manage_users_dialog(company_id: int):
    st.subheader("Company Users")
    users = APIClient.get_users(company_id)

    if users:
        for u in users:
            st.markdown(f"- **{u.get('username')}** ({u.get('role', 'user')})")
    else:
        st.info("No users found.")

    st.divider()
    st.markdown("#### Add User")
    new_username = st.text_input("Username", key="new_user_name")
    new_password = st.text_input("Password", type="password", key="new_user_pass")
    role = st.selectbox("Role", ["user", "admin"])

    if st.button("Add User", type="primary"):
        if new_username and new_password:
            if APIClient.create_user(company_id, new_username, new_password, role):
                st.success("User added!")
                st.rerun()
            else:
                st.error("Error creating user. Username might be taken.")
        else:
            st.error("Please fill all fields.")
