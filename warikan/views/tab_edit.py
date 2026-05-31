import datetime
import time

import streamlit as st

from warikan.db import delete_payment, get_all_payments, get_payment, get_payment_details, update_payment
from warikan.i18n import t


def render_tab_edit():
    st.subheader(t("tab_edit.subheader"))
    st.write(t("tab_edit.description"))

    all_payments = get_all_payments()

    if len(all_payments) > 0:
        payment_options = {
            t("tab_edit.event_option", date=row[1], location=row[2]): row[0] for row in all_payments
        }
        selected_event_label = st.selectbox(t("tab_edit.select_label"), list(payment_options.keys()))
        selected_payment_id = payment_options[selected_event_label]

        p_date, p_loc = get_payment(selected_payment_id)
        details = get_payment_details(selected_payment_id)

        st.write("---")
        st.write(t("tab_edit.edit_header"))

        edit_date = st.date_input(
            t("tab_edit.date_label"),
            datetime.datetime.strptime(p_date, "%Y-%m-%d").date(),
            key="edit_date",
        )
        edit_location = st.text_input(t("tab_edit.location_label"), value=p_loc, key="edit_loc")

        st.write(t("tab_edit.amount_prompt"))
        edit_amounts = {}
        for detail_id, member_name, amount in details:
            edit_amounts[detail_id] = st.number_input(
                t("tab_edit.amount_label", member=member_name),
                min_value=0,
                value=amount,
                step=50,
                key=f"edit_amt_{detail_id}",
            )

        col_update, col_delete = st.columns(2)

        with col_update:
            if st.button(t("tab_edit.update_button"), type="primary", key="btn_update"):
                with st.spinner(t("tab_edit.update_spinner")):
                    update_payment(selected_payment_id, edit_date, edit_location, edit_amounts)
                    time.sleep(0.5)
                st.success(t("tab_edit.update_success"))
                st.rerun()

        with col_delete:
            if st.button(t("tab_edit.delete_button"), type="secondary", key="btn_delete"):
                with st.spinner(t("tab_edit.delete_spinner")):
                    delete_payment(selected_payment_id)
                    time.sleep(0.5)
                st.error(t("tab_edit.delete_success"))
                st.rerun()
    else:
        st.info(t("tab_edit.no_data"))
