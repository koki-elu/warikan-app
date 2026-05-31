import streamlit as st

from warikan.db import init_db, set_default_members
from warikan.i18n import t
from warikan.views.sidebar import render_sidebar
from warikan.views.tab_edit import render_tab_edit
from warikan.views.tab_input import render_tab_input
from warikan.views.tab_settled import render_tab_settled
from warikan.views.tab_unpaid import render_tab_unpaid

init_db()
set_default_members()

st.title(t("app.title"))

tab1, tab2, tab3, tab4 = st.tabs([
    t("tabs.input"),
    t("tabs.unpaid"),
    t("tabs.settled"),
    t("tabs.edit"),
])

current_members = render_sidebar()

with tab1:
    render_tab_input(current_members)

with tab2:
    render_tab_unpaid(current_members)

with tab3:
    render_tab_settled(current_members)

with tab4:
    render_tab_edit()
