import streamlit as st

from warikan.db import get_unpaid_details, settle_detail
from warikan.i18n import t


def _member_unpaid_details(member, unpaid_details):
    return [
        (detail_id, p_date, p_loc, amt)
        for detail_id, m_name, p_date, p_loc, amt in unpaid_details
        if m_name == member
    ]


def _render_settle_row(detail_id, p_date, p_loc, amt):
    col_md, col_btn = st.columns([4, 2])
    with col_md:
        st.write(t("tab_unpaid.detail", date=p_date, location=p_loc, amount=amt))
    with col_btn:
        if st.button(t("tab_unpaid.settle_button"), key=f"pay_{detail_id}"):
            with st.spinner(t("tab_unpaid.spinner")):
                settle_detail(detail_id)
            st.rerun()


def _render_member_unpaid(member, unpaid_details):
    member_details = _member_unpaid_details(member, unpaid_details)
    member_total = sum(amt for _, _, _, amt in member_details)

    if member_total > 0:
        st.write(t("tab_unpaid.member_total", member=member, total=member_total))
        with st.expander(t("tab_unpaid.expander")):
            for detail_id, p_date, p_loc, amt in member_details:
                _render_settle_row(detail_id, p_date, p_loc, amt)
    else:
        st.write(t("tab_unpaid.no_unpaid", member=member))


def render_tab_unpaid(current_members):
    st.subheader(t("tab_unpaid.subheader"))

    unpaid_details = get_unpaid_details()

    if not current_members:
        st.info(t("tab_unpaid.no_members"))
        return

    for member in current_members:
        _render_member_unpaid(member, unpaid_details)