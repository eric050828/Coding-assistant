import streamlit as st
from st_pages import add_page_title
from utils.vectorDB import *

add_page_title()

if "problem_id" in st.session_state:
    code_id = st.text_input("以ID搜尋")
    col1, options = st.columns([5, 1])
    with options:
        show_id = st.checkbox("顯示ID")
        show_embedding = st.checkbox("顯示embedding")
        show_metadata = st.checkbox("顯示metadata")

    with col1:
        data = show_codes_data(
            st.session_state["problem_id"], 
            show_ids=show_id, 
            where={"id":code_id} if code_id else None,
        )
        col1.markdown(f"共{len(data)}筆程式碼")

        for i in range(len(data)):
            if show_id:data[i][0]
            code = data[i][1].replace("\n\n", "\n") if show_id else data[i].replace("\n\n", "\n")
            st.code(code, "python", line_numbers=True)
            st.divider()
            
        
else:
    st.warning("你還沒上傳題目")