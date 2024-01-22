import streamlit as st
from streamlit_ace import st_ace, LANGUAGES, THEMES
from st_pages import Page, show_pages, add_page_title

from utils.chatbot import generate_response
from utils.file import *

add_page_title()

source_code_path = st.sidebar.selectbox(
    "選擇驗證測資程式",
    ["main.py"]
    # list_files("code")
)

file_name = st.text_input(
    "檔案名稱",
    value=source_code_path if source_code_path else "main.py",
    placeholder="請輸入檔案名稱加上副檔名",
    key="file_name",
)
if source_code_path and st.sidebar.button("刪除"):
    st.sidebar.warning(f"確定刪除 {source_code_path}?")
    # st.sidebar.button("確定", on_click=delete_file, args=(f"code/{source_code_path}",))
    st.sidebar.button("取消")

codeblock, settings = st.columns([3, 1])
settings.subheader("編輯區塊設定")
language = settings.selectbox("程式語言", options=LANGUAGES, index=121)
theme = settings.selectbox("編輯區塊主題", options=THEMES, index=35)
font_size = settings.slider("文字大小", 5, 24, 14)
tab_size = settings.slider("Tab 大小", 1, 8, 4)
show_gutter = settings.checkbox("顯示行號", value=True)
show_print_margin = settings.checkbox("顯示列印邊距", value=False)
wrap = settings.checkbox("換行", value=False)
readonly = settings.checkbox("唯讀模式", value=False)

source_code = open_file("code", source_code_path).replace("\n\n", "\n") if source_code_path else ""
with codeblock:
    code = st_ace(
        source_code,
        placeholder="輸入驗證測資程式碼",
        language=language or "python",
        theme=theme,  # type: ignore
        keybinding="vscode",
        font_size=font_size,
        tab_size=tab_size,
        show_gutter=show_gutter,
        show_print_margin=show_print_margin,
        wrap=wrap,
        auto_update=True,
        readonly=readonly,
        min_lines=25,
        key="editor_code_block",
    )
    if code and st.button("儲存"):
        save_file("code", file_name, code.replace("\n\n", "\n"))
        st.success(f"已儲存程式碼: {file_name}")
        st.subheader("已儲存程式碼預覽")
        st.code(code, "python", line_numbers=True)
    

if "problem_id" in st.session_state:
    question = st.text_input("輸入問題或錯誤訊息", placeholder="此處可空白")
    if st.button("詢問"):
        response = generate_response(
            st.session_state["problem_id"], 
            question, 
            code, 
            st.session_state["problem_description"]
        )
        response["result"]
        for document in response["source_documents"]:
            st.code(
                document.page_content.replace("\n\n", "\n"),
                language="python",
                line_numbers=True
            )