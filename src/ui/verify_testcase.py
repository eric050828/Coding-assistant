import os
import time
import streamlit as st

from streamlit_ace import st_ace
from judge0 import Judge0Client
from utils.file import (
    list_folder,
    open_file,
    list_files,
    pair_files,
)
from utils.text import generate_diff


st.set_page_config(page_title="驗證測資", page_icon="▶️")
st.title("驗證測資")

st.sidebar.header("驗證測資程式")
source_code_path = st.sidebar.selectbox(
    "選擇驗證測資程式",
    list_files("code"),
)
source_code = open_file("code", source_code_path) if source_code_path else ""

with st.expander("顯示程式碼"):
    st.code(source_code, line_numbers=True)

@st.cache_resource
def new_judge_client():
    return Judge0Client()


judge_client = new_judge_client()

languages_data = judge_client.get_languages()
language_map = {language["name"]: language["id"] for language in languages_data}

folder_option = st.selectbox("選擇測資類型", list_folder("data"))
language = st.selectbox(
    "選擇程式語言",
    options=list(sorted(language_map.keys(), reverse=True)),
    index=8,
)
language_id = language_map[language]
show_path, show_count, exec_bt, batch_bt = st.columns(4)

files = []
data_folder = None  
if folder_option is not None:
    data_folder = os.path.join("data", folder_option)
    show_path.write(data_folder)
    files = list_folder(data_folder)
    case_count = int(len(files) // 2)
    show_count.write(f"共有 {case_count} 筆測資")

st.divider()



if data_folder and exec_bt.button("個別執行驗證"):
    with st.spinner("執行中..."):
        st.subheader("程式輸出與測資答案差異")
        for infile, ansfile in pair_files(files):
            number = int(infile.split("/")[-1].split(".")[0])
            in_data = open_file(data_folder, infile)
            ans_data = open_file(data_folder, ansfile)
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
                st.success(submission["status"]["description"])
            else:
                st.error(submission["status"]["description"])

            if stderr:
                st.error(stderr)
                st.divider()

            if compile_output:
                st.error(compile_output)
                st.divider()

            if stdout:
                diff_left, diff_right = generate_diff(stdout, ans_data)
                left_block, right_block = st.columns(2)
                with left_block:
                    st.write(f"{infile} 測資，程式輸出:")
                    st_ace(
                        diff_left,
                        language="diff",
                        auto_update=True,
                        readonly=True,
                        key=f"left_block_ace_{number}",
                    )

                with right_block:
                    st.write(f"{ansfile} 測資答案:")
                    st_ace(
                        diff_right,
                        language="diff",
                        auto_update=True,
                        readonly=True,
                        key=f"right_block_ace_{number}",
                    )


if data_folder and batch_bt.button("批次執行驗證"):
    with st.spinner("執行中..."):
        st.subheader("程式輸出與測資答案差異")
        data = []
        testcases = []
        for infile, ansfile in pair_files(files):
            in_data = open_file(data_folder, infile)
            ans_data = open_file(data_folder, ansfile)
            payload = {
                "source_code": source_code,
                "language_id": language_id,
                "stdin": in_data,
                "expected_output": ans_data,
            }
            data.append(payload)
            testcases.append([in_data, ans_data])
        submissions_result = judge_client.create_batch_submissions(data)
        submission_tokens = [
            result["token"] 
            for result in submissions_result
            if "token" in result
        ]
        if submission_tokens:
            tokens_string = ",".join(submission_tokens)
            submissions = judge_client.get_batch_submissions(tokens_string)
            count = len([
                submission
                for submission in submissions["submissions"]
                if submission["status"]["id"] >= 3
            ])
            while count < len(submission_tokens):
                submissions = judge_client.get_batch_submissions(tokens_string)
                count = len([
                    submission
                    for submission in submissions["submissions"]
                    if submission["status"]["id"] >= 3
                ])
                st.toast(f"已完成 {count} 筆測資")
                time.sleep(1)
            
            st.toast("已完成所有測資")
            for idx, submission in enumerate(submissions["submissions"]):
                in_data, ans_data = testcases[idx]
                stdout = submission["stdout"]
                exec_time = submission["time"]
                exec_memory = submission["memory"]
                stderr = submission["stderr"]
                compile_output = submission["compile_output"]
                st.divider()
                
                if submission["status"]["id"] == 3:
                    st.success(submission["status"]["description"])
                else:
                    st.error(submission["status"]["description"])

                if stderr:
                    st.error(stderr)
                    st.divider()

                if compile_output:
                    st.error(compile_output)
                    st.divider()

                if stdout:
                    diff_left, diff_right = generate_diff(stdout, ans_data)
                    left_block, right_block = st.columns(2)
                    with left_block:
                        st.write("程式輸出:")
                        st_ace(
                            diff_left,
                            language="diff",
                            auto_update=True,
                            readonly=True,
                            key=f"left_block_ace_b{idx}",
                        )

                    with right_block:
                        st.write("測資答案:")
                        st_ace(
                            diff_right,
                            language="diff",
                            auto_update=True,
                            readonly=True,
                            key=f"right_block_ace_b{idx}",
                        )
            