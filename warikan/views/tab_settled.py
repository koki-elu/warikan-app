import streamlit as st

from warikan.db import get_settled_details
from warikan.i18n import t


def render_tab_settled(current_members):
    st.subheader(t("tab_settled.subheader"))
    settled_details = get_settled_details()

    if len(settled_details) > 0:
        filter_options = [t("tab_settled.filter_all")] + current_members
        selected_user = st.selectbox(t("tab_settled.filter_label"), filter_options)
        st.write("---")

        display_count = 0
        for p_date, p_loc, m_name, amt in settled_details:
            if selected_user == t("tab_settled.filter_all") or m_name == selected_user:
                st.write(t("tab_settled.history_item", date=p_date, location=p_loc, member=m_name, amount=amt))
                display_count += 1

        if display_count == 0:
            st.caption(t("tab_settled.no_history_for_member", member=selected_user))
    else:
        st.caption(t("tab_settled.no_data"))
