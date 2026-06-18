import streamlit as st
from services import db_services
from services.workflows import template_workflows

@st.dialog("Edit Template")
def edit_template_dialog(tpl):
    st.write("Edit template settings")
    info = st.text_input("Template Name / Info", value=tpl.get('template_info', ''))
    
    ratio_options = ["1:1", "4:5", "16:9", "9:16"]
    current_ratio = tpl.get('aspect_ratio', '1:1')
    ratio_idx = ratio_options.index(current_ratio) if current_ratio in ratio_options else 0
    aspect_ratio = st.selectbox("Aspect Ratio", ratio_options, index=ratio_idx)
    
    constraints = st.text_area("Template Constraints (Visuals, fonts, etc.)", value=tpl.get('template_constraints', ''))
    
    if st.button("Save Changes", type="primary"):
        if not info:
            st.error("Please provide template info.")
            return
            
        update_data = {
            "template_info": info,
            "aspect_ratio": aspect_ratio,
            "template_constraints": constraints
        }
        res = template_workflows.update_template_details(tpl['id'], update_data)
        if res.get("success"):
            st.success("Template updated successfully!")
            st.rerun()
        else:
            st.error(res.get("error"))

def render():
    st.title("Templates")
    user = st.session_state.get('user', {})
    
    if user.get('role') == 'admin' and not user.get('company_id'):
        st.info("Admins must select a company to view templates.", icon=":material/info:")
        if st.button("Go to Companies Dashboard", icon=":material/arrow_forward:"):
            st.switch_page(st.session_state['pages_dict']['admin_dashboard'])
        return

    company_id = user.get('company_id')

    # Initialize template creation state
    st.session_state.setdefault('template_create_mode', None)
    st.session_state.setdefault('template_ai_result', None)
    st.session_state.setdefault('template_ai_modified', None)

    # ─── Create New Template ───────────────────────────────────────
    with st.expander("Create New Template", icon=":material/add:", expanded=st.session_state.template_create_mode is not None):
        _render_create_template(company_id)

    # ─── Existing Templates List ──────────────────────────────────
    st.subheader("Your Templates", divider="gray")

    templates = db_services.get_templates(company_id)
    
    if not templates:
        st.info("No templates found. Create your first template above!", icon=":material/info:")
        return
        
    for tpl in templates:
        with st.container(border=True):
            t_cols = st.columns([1, 3, 1])

            with t_cols[0]:
                tpl_url = tpl.get('template_url')
                if tpl_url:
                    st.image(tpl_url, width=120)
                else:
                    st.markdown(
                        "<div style='width:120px;height:90px;background:#1e293b;border-radius:8px;"
                        "display:flex;align-items:center;justify-content:center;color:#64748b;"
                        "font-size:11px;'>No preview</div>",
                        unsafe_allow_html=True
                    )

            with t_cols[1]:
                st.markdown(f"**{tpl.get('template_info', 'Unnamed Template')}**")
                st.caption(f"Aspect Ratio: {tpl.get('aspect_ratio', 'N/A')}")
                constraints = tpl.get('template_constraints', '')
                if constraints:
                    display_constraints = constraints[:150] + "..." if len(constraints) > 150 else constraints
                    st.caption(f"Constraints: {display_constraints}")

            with t_cols[2]:
                if st.button("Edit", key=f"edit_tpl_{tpl['id']}", icon=":material/edit:"):
                    edit_template_dialog(tpl)
                if st.button("Delete", key=f"delete_tpl_{tpl['id']}", icon=":material/delete:"):
                    if db_services.delete_template(tpl['id']):
                        st.success("Deleted successfully!")
                        st.rerun()

def _render_create_template(company_id):
    """Render the template creation section with AI/Manual paths."""

    # Step 1: Choose AI or Manual
    if st.session_state.template_create_mode is None:
        st.markdown("**Choose creation method:**")
        mode = st.segmented_control(
            "Template creation mode",
            options=["Manual", "AI Generation"],
            label_visibility="collapsed",
            key="template_mode_selector"
        )
        if mode == "Manual":
            st.session_state.template_create_mode = 'manual'
            st.rerun()
        elif mode == "AI Generation":
            st.session_state.template_create_mode = 'ai'
            st.rerun()
        return

    # Reset button
    if st.button("Reset", icon=":material/restart_alt:", key="reset_template_create"):
        st.session_state.template_create_mode = None
        st.session_state.template_ai_result = None
        st.session_state.template_ai_modified = None
        st.rerun()

    # ─── Manual Path ──────────────────────────────────────────────
    if st.session_state.template_create_mode == 'manual':
        _render_manual_template(company_id)

    # ─── AI Path ──────────────────────────────────────────────────
    elif st.session_state.template_create_mode == 'ai':
        _render_ai_template(company_id)

def _render_manual_template(company_id):
    """Manual template creation: upload image and fill details."""
    st.markdown("**Manual Template Creation**")

    info = st.text_input("Template Name / Info", key="manual_tpl_info")
    aspect_ratio = st.selectbox("Aspect Ratio", ["1:1", "4:5", "16:9", "9:16"], key="manual_tpl_ratio")
    constraints = st.text_area("Template Constraints (Visuals, fonts, etc.)", key="manual_tpl_constraints")

    uploaded = st.file_uploader("Upload template image", type=["png", "jpg", "jpeg", "webp"], key="manual_tpl_upload")
    if uploaded:
        st.image(uploaded, width=250, caption="Template preview")

    if st.button("Save Template", icon=":material/save:", type="primary", key="save_manual_tpl"):
        if not info:
            st.error("Please provide template info/name.")
            return

        with st.spinner("Saving manual template..."):
            img_bytes = uploaded.getvalue() if uploaded else None
            res = template_workflows.save_manual_template(company_id, info, aspect_ratio, constraints, img_bytes)
            
            if res.get("success"):
                st.success("Template created successfully!")
                st.session_state.template_create_mode = None
                st.rerun()
            else:
                st.error(res.get("error"))

def _render_ai_template(company_id):
    """AI template creation: prompt, optional ref image, name, ratio, generate, and modify."""
    st.markdown("**AI Template Generation**")

    col1, col2 = st.columns(2)
    with col1:
        ai_prompt = st.text_area(
            "Describe the template you want",
            placeholder="e.g. A clean social media template with a modern gradient...",
            height=120,
            key="ai_tpl_prompt"
        )
        ai_name = st.text_input("Template Name", key="ai_tpl_name")

    with col2:
        ratio_options = ["1:1", "4:5", "16:9", "9:16"]
        ai_ratio = st.selectbox("Aspect Ratio", ratio_options, key="ai_tpl_ratio")
        ai_constraints = st.text_input("Additional constraints (optional)", key="ai_tpl_constraints")

    ref_image = st.file_uploader("Upload reference image (optional)", type=["png", "jpg", "jpeg", "webp"], key="ai_tpl_ref")
    if ref_image:
        st.image(ref_image, width=200, caption="Reference image")

    # Generate button
    if st.button("Generate Template", icon=":material/auto_awesome:", type="primary", key="gen_ai_tpl"):
        if not ai_prompt:
            st.error("Please enter a prompt.")
        elif not ai_name:
            st.error("Please enter a template name.")
        else:
            with st.spinner("Generating template with AI..."):
                res = template_workflows.generate_ai_template(ai_prompt, ai_name, ai_ratio, company_id)
                if res.get("success"):
                    st.session_state.template_ai_result = res["data"]
                    st.session_state.template_ai_result["constraints"] = ai_constraints
                    st.rerun()
                else:
                    st.error(res.get("error"))

    # Show generated result
    if st.session_state.template_ai_result:
        result = st.session_state.template_ai_result
        st.subheader("Generated Template", divider="gray")

        # Side-by-side: current vs modified (if modification was done)
        if st.session_state.template_ai_modified:
            comp_cols = st.columns(2)
            with comp_cols[0]:
                st.caption("Original Generated")
                st.image(result['bytes'], width=250)
            with comp_cols[1]:
                st.caption("Modified Version")
                st.image(st.session_state.template_ai_modified, width=250)

            mod_cols = st.columns(3)
            with mod_cols[0]:
                if st.button("Use modified version", icon=":material/check:", type="primary", key="use_modified_tpl"):
                    result['bytes'] = st.session_state.template_ai_modified
                    st.session_state.template_ai_modified = None
                    st.rerun()
            with mod_cols[1]:
                if st.button("Keep original", icon=":material/undo:", key="keep_original_tpl"):
                    st.session_state.template_ai_modified = None
                    st.rerun()
        else:
            st.image(result['bytes'], width=300, caption=f"Template: {result['name']}")

        # Modification prompt
        st.markdown("**Modify template with AI:**")
        mod_prompt = st.text_input("Modification prompt", placeholder="e.g. Make the colors warmer...", key="tpl_mod_prompt")
        if st.button("Modify", icon=":material/auto_fix_high:", key="modify_tpl_btn"):
            if mod_prompt:
                with st.spinner("Modifying template with AI..."):
                    res = template_workflows.modify_ai_template(
                        result['prompt'], mod_prompt, result['ratio'], company_id
                    )
                    if res.get("success"):
                        st.session_state.template_ai_modified = res["data"]
                        st.rerun()
                    else:
                        st.error(res.get("error"))

        # Save button
        if st.button("Save Template to Database", icon=":material/save:", type="primary", key="save_ai_tpl"):
            with st.spinner("Saving template..."):
                res = template_workflows.save_generated_template(
                    company_id, result['name'], result['ratio'], result.get('constraints', ''), result['bytes']
                )
                if res.get("success"):
                    st.success("Template saved successfully!")
                    st.session_state.template_ai_result = None
                    st.session_state.template_ai_modified = None
                    st.session_state.template_create_mode = None
                    st.rerun()
                else:
                    st.error(res.get("error"))
