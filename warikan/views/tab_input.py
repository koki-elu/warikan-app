import datetime
import time

import streamlit as st

from warikan.db import create_payment
from warikan.i18n import t


def render_tab_input(current_members):
    st.subheader(t("tab_input.subheader"))
    date = st.date_input(t("tab_input.date_label"), datetime.date.today())
    location = st.text_input(t("tab_input.location_label"), placeholder=t("tab_input.location_placeholder"))

    st.write(t("tab_input.amount_prompt"))
    if len(current_members) == 0:
        st.info(t("tab_input.no_members"))
    else:
        cols = st.columns(min(len(current_members), 4))
        member_amounts = {}
        for i, member in enumerate(current_members):
            with cols[i % 4]:
                amount = st.number_input(
                    t("tab_input.amount_label", member=member),
                    min_value=0,
                    step=50,
                    value=0,
                    key=f"amt_{member}",
                )
                if amount > 0:
                    member_amounts[member] = amount

        total_amount = sum(member_amounts.values())
        st.metric(label=t("tab_input.total_label"), value=t("tab_input.total_value", amount=total_amount))

        if st.button(t("tab_input.submit_button"), type="primary"):
            if total_amount == 0:
                st.error(t("tab_input.error_zero"))
            else:
                with st.spinner(t("tab_input.spinner")):
                    create_payment(date, location, member_amounts)
                    time.sleep(0.5)

                st.success(t("tab_input.success", location=location))
                st.rerun()
