"""Shared image placeholder component."""
import streamlit as st


def render_image_placeholder(height: str = "260px") -> None:
    """Render a dark styled placeholder when no image exists."""
    st.markdown(
        f"<div style='"
        f"width:100%;min-height:{height};background:#0f172a;border-radius:12px;"
        f"display:flex;flex-direction:column;align-items:center;justify-content:center;"
        f"color:#64748b;font-size:14px;border:1px dashed #334155;"
        f"'>"
        f"<span style='font-size:36px;'>&#128339;</span>"
        f"<span style='margin-top:8px;'>Image Pending</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
