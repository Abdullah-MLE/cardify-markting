"""Shared Calendar View component."""
import streamlit as st
import calendar
from datetime import datetime


def _change_month(step):
    """Callback to update view_date by month steps"""
    current_date = st.session_state.view_date
    year = current_date.year
    month = current_date.month

    new_month = month + step
    new_year = year

    if new_month < 1:
        new_month = 12
        new_year -= 1
    elif new_month > 12:
        new_month = 1
        new_year += 1

    st.session_state.view_date = datetime(new_year, new_month, 1).date()
    if "quick_nav_date" in st.session_state:
        st.session_state.quick_nav_date = st.session_state.view_date


def get_month_grid(year, month):
    """Generates calendar grid aligned to Saturday start"""
    num_days = calendar.monthrange(year, month)[1]
    first_day_weekday = datetime(year, month, 1).weekday()

    # Offset to start week on Saturday (Monday=0 ... Saturday=5, Sunday=6)
    start_offset = (first_day_weekday + 2) % 7

    month_grid = [None] * start_offset
    for day in range(1, num_days + 1):
        month_grid.append(datetime(year, month, day).date())

    return month_grid


def render_calendar_view(scheduled_content, company_id):
    """Renders the calendar UI for scheduled content."""
    view_date = st.session_state.view_date
    year = view_date.year
    month = view_date.month
    today_date = datetime.now().date()

    # 1. Header & Navigation
    col_header, col_nav = st.columns([5, 1.5])

    with col_header:
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        st.markdown(
            f"<h2 style='text-align: center; margin: 0;'>{month_names[month-1]} {year}</h2>",
            unsafe_allow_html=True,
        )

    with col_nav:
        selected_nav_date = st.date_input(
            "Jump to date",
            value=st.session_state.view_date,
            label_visibility="collapsed",
            key="quick_nav_date",
        )
        if selected_nav_date != st.session_state.view_date:
            st.session_state.view_date = selected_nav_date
            st.rerun()

    # Days header starting on Saturday
    days_names = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]

    st.write("---")

    # Render week day names
    header_cols = st.columns(7)
    for i, name in enumerate(days_names):
        header_cols[i].markdown(
            f"<div style='text-align: center; font-weight: bold; background-color: #1e293b; color: #f8fafc; padding: 8px; border-radius: 6px; margin-bottom: 10px;'>{name}</div>",
            unsafe_allow_html=True,
        )

    month_grid = get_month_grid(year, month)

    # Render calendar grid
    for i in range(0, len(month_grid), 7):
        week_days = month_grid[i : i + 7]
        cols = st.columns(7)

        for j, day_date in enumerate(week_days):
            with cols[j]:
                if day_date:
                    is_past = day_date < today_date
                    is_today = day_date == today_date

                    # Filter content for this specific date
                    day_posts = [p for p in scheduled_content if p.get("publish_date") == str(day_date)]

                    with st.container(border=True):
                        # Header of cell
                        header_style = "font-size: 13px; text-align: center; display: block; margin-bottom: 5px;"
                        if is_today:
                            header_style += " color: #ff4b4b; font-weight: bold;"
                        elif is_past:
                            header_style += " color: #64748b;"
                        else:
                            header_style += " color: #f8fafc;"

                        st.markdown(
                            f"<div style='text-align: center;'>"
                            f"<span style='{header_style}'>{days_names[j]} {day_date.day}/{day_date.month}</span>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                        # Post content / Preview
                        if day_posts:
                            first_post = day_posts[0]
                            post_images = first_post.get("post_images")
                            thumb_url = post_images[0] if post_images and isinstance(post_images, list) else None

                            if thumb_url:
                                st.image(thumb_url)
                            else:
                                st.markdown(
                                    "<div style='height: 80px; display: flex; align-items: center; justify-content: center; color: gray; font-size: 11px;'>No Image</div>",
                                    unsafe_allow_html=True,
                                )

                            if len(day_posts) > 1:
                                st.markdown(
                                    f"<div style='text-align: center; color: #3b82f6; font-size: 11px; margin-top: 4px; font-weight: bold;'>"
                                    f"➕ {len(day_posts) - 1} more post(s)"
                                    f"</div>",
                                    unsafe_allow_html=True,
                                )
                        else:
                            color = "#64748b" if is_past else "#475569"
                            st.markdown(
                                f"<div style='height: 80px; display: flex; align-items: center; justify-content: center; color: {color}; font-size: 11px;'>Empty</div>",
                                unsafe_allow_html=True,
                            )

                        # Buttons
                        if not is_past:
                            b_cols = st.columns(2)
                            with b_cols[0]:
                                if st.button("✏️", key=f"edit_day_{day_date}", help="View/Edit"):
                                    st.session_state.selected_date = day_date
                                    st.switch_page(st.session_state["pages_dict"]["day_details"])
                            with b_cols[1]:
                                if st.button("➕", key=f"create_day_{day_date}", help="Create post"):
                                    st.session_state.selected_date = day_date
                                    st.switch_page(st.session_state["pages_dict"]["create_content"])
                        else:
                            if st.button("👁️", key=f"view_day_{day_date}", help="View posts"):
                                st.session_state.selected_date = day_date
                                st.switch_page(st.session_state["pages_dict"]["day_details"])
                else:
                    st.markdown(
                        "<div style='border: 1px dashed #334155; min-height: 120px; border-radius: 6px; margin-bottom: 8px;'></div>",
                        unsafe_allow_html=True,
                    )

    # Bottom navigation
    st.write("---")
    col_prev, _, col_next = st.columns([2, 4, 2])
    with col_prev:
        st.button("← Previous Month", key="prev_month_btn", on_click=_change_month, args=(-1,))
    with col_next:
        st.button("Next Month →", key="next_month_btn", on_click=_change_month, args=(1,))
