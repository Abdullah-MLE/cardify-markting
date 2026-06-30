"""Shared mini content card component."""
import streamlit as st

TYPE_COLORS = {"post": "blue", "story": "violet", "carousel": "orange"}
TYPE_ICONS = {"post": "📝", "story": "📖", "carousel": "🎠"}


def parse_h1(h1_value) -> str:
    """Convert h1 (list or str) to display string."""
    if isinstance(h1_value, list):
        return ", ".join(h1_value) if h1_value else ""
    return str(h1_value) if h1_value else ""


def render_mini_card(item: dict, on_view_key_suffix: str = "") -> None:
    """
    Render a compact card row for a single content item.
    Clicking 'View' navigates to content_details page.
    """
    with st.container(border=True):
        cols = st.columns([2, 3, 1, 1])

        with cols[0]:
            ctype = item.get("content_type", "post")
            st.badge(
                ctype.capitalize(),
                icon=":material/circle:",
                color=TYPE_COLORS.get(ctype, "gray"),
            )

        with cols[1]:
            headline = parse_h1(item.get("h1"))
            display = headline[:50] + "..." if len(headline) > 50 else headline
            st.markdown(f"**{display or 'No headline'}**")

        with cols[2]:
            st.caption(item.get("publish_time", "") or "")

        with cols[3]:
            key = f"mini_view_{item['id']}_{on_view_key_suffix}"
            if st.button("View", key=key, icon=":material/open_in_new:"):
                st.session_state.selected_content_id = item["id"]
                st.switch_page(st.session_state["pages_dict"]["content_details"])
