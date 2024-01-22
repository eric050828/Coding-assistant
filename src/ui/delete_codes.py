import streamlit as st
from st_pages import add_page_title
from utils.vectorDB import *


add_page_title()

if "problem_id" in st.session_state:
    col1, col2, col3 = st.columns([5, 1, 1])
    code_id = col1.text_input(label="輸入程式碼ID")
    col2.button("確定刪除", on_click=delete_codes, args=(st.session_state["problem_id"], [code_id]))
    if code_id:
        code = show_codes_data(
            st.session_state["problem_id"], 
            where={"ids":code_id},
        )
        if code: 
            st.markdown("程式碼預覽")
            st.code(code, "python", line_numbers=True)
        else:
            st.warning("找不到程式碼")
    
    ids = show_codes_data(st.session_state["problem_id"], show_ids=True, show_documents=False)
    st.table(ids)
    if st.button("刪除全部", type="primary"):
        st.warning(f"此次執行將會刪除{len(ids)}筆資料，確定要刪除嗎?")
        col1, col2 = st.columns([6, 1])
        col1.button("確定", on_click=delete_codes, args=(st.session_state["problem_id"], ids))
        col2.button("取消", type="primary")
else:
    st.warning("你還沒上傳題目")