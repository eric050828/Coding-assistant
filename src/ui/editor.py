import streamlit as st
from streamlit_ace import st_ace, LANGUAGES, THEMES
from st_pages import Page, show_pages, add_page_title

from utils.chatbot import generate_response
from utils.file import *
from utils.text import generate_diff
from judge0 import Judge0Client

import time


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
            

@st.cache_resource
def new_judge_client():
    return Judge0Client()


judge_client = new_judge_client()

languages_data = judge_client.get_languages()
language_map = {language["name"]: language["id"] for language in languages_data}
st.subheader("執行驗證測資程式")

in_data, ans_data = "", ""
sample_path = "dom/data/sample"
if folder_exists(sample_path):
    files = list_folder(sample_path)
    infile, ansfile = pair_files(files)[0]
    in_data = open_file(sample_path, infile)
    ans_data = open_file(sample_path, ansfile)


language = st.selectbox(
    "選擇程式語言",
    options=list(sorted(language_map.keys(), reverse=True)),
    index=8,
)
language_id = language_map[language]
input_block, ans_block = st.columns(2)
with input_block:
    st.write("測試測資")
    in_data = st_ace(in_data, height=200, auto_update=True, key="in_data_ace")

with ans_block:
    st.write("測資答案")
    ans_data = st_ace(ans_data, height=200, auto_update=True, key="ans_data_ace")

if st.button("執行"):
    with st.spinner("執行中..."):
        submission = judge_client.create_submission(
            source_code,
            language_id,
            stdin=in_data,
            expected_output=ans_data,
        )
        submission_id = submission["token"]
        submission = judge_client.get_submission(submission_id)
        while submission["status"]["id"] <= 2:
            submission = judge_client.get_submission(submission_id)
            st.toast(submission["status"]["description"])
            time.sleep(1)
        # st.write(submission)
        stdout = submission["stdout"]
        exec_time = submission["time"]
        exec_memory = submission["memory"]
        stderr = submission["stderr"]
        compile_output = submission["compile_output"]
        st.divider()
        if submission["status"]["id"] == 3:
            exec_time_block, exec_memory_block = st.columns(2)
            exec_time_block.metric(label="程式執行時間", value=f"{exec_time} 秒")
            if exec_memory > 1024:
                exec_memory = exec_memory / 1024
                exec_memory_block.metric(label="記憶體使用量", value=f"{exec_memory:.2f} MB")
            else:
                exec_memory_block.metric(label="記憶體使用量", value=f"{exec_memory} KB")
            st.divider()
        
        if submission["status"]["id"] == 3:
            st.success(submission["status"]["description"])
        else:
            st.error(submission["status"]["description"])
            st.json(submission)
        st.divider()

        if stderr:
            st.error(stderr)
            st.divider()

        if compile_output:
            st.error(compile_output)
            st.divider()

        if stdout:
            diff_left, diff_right = generate_diff(stdout, ans_data)
            st.subheader("程式輸出與測資答案差異")
            left_block, right_block = st.columns(2)
            with left_block:
                st.write("程式輸出:")
                st.caption("- 表示程式輸出錯誤")
                st_ace(
                    diff_left,
                    language="diff",
                    auto_update=True,
                    readonly=True,
                    theme=theme,  # type: ignore
                    key="left_block_ace",
                )

            with right_block:
                st.write("測資答案:")
                st.caption("+ 表示測資正確答案")
                st_ace(
                    diff_right,
                    language="diff",
                    auto_update=True,
                    readonly=True,
                    theme=theme,  # type: ignore
                    key="right_block_ace",
                )