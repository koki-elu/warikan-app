import streamlit as st

from warikan.db import add_member, get_members
from warikan.i18n import t


def render_sidebar():
    st.sidebar.title(t("sidebar.title"))
    current_members = get_members()

    new_member = st.sidebar.text_input(t("sidebar.add_label"), placeholder=t("sidebar.add_placeholder"))
    if st.sidebar.button(t("sidebar.add_button")):
        if new_member and new_member not in current_members:
            add_member(new_member)
            st.sidebar.success(t("sidebar.add_success", name=new_member))
            st.rerun()

    return current_members
