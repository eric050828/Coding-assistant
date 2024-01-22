import streamlit as st
from st_pages import add_page_title

from utils.vectorDB import *
from utils.file import *


def upload_code_files(collection_name, codes):
    file_paths = save_uploaded_code_files(codes)
    store_codes(collection_name, file_paths)
    st.info(f"已成功上傳{len(codes)}筆程式碼")

add_page_title()

if "problem_id" in st.session_state:
    codes = st.file_uploader("上傳程式碼", "py", True, )
    col1, col2 = st.columns([1, 9])
    col1.button("上傳", on_click=upload_code_files, args=(st.session_state["problem_id"], codes), type="primary")
    st.markdown("### 程式碼預覽")
    if codes:
        for code in codes:
            source_code = code.getvalue().decode('utf-8').replace('\\n', '\n')
            st.code(source_code, "python", line_numbers=True)

else:
    st.warning("你還沒上傳題目")