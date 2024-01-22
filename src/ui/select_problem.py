import streamlit as st
from st_pages import add_page_title
from utils.vectorDB import *
from utils.file import *

from pathlib import Path
import zipfile

def save_file(problem_id, uploaded_problem_zip):
    if not problem_id:
        st.warning("題目代號為必填")
        return
    if not uploaded_problem_zip:
        st.warning("你還沒上傳zip")
        return
    
    file_name = str(uploaded_problem_zip.name).split(".")[0]
    # unzip files and folder to temp folder and save to session state
    tmp_folder = get_tmp_folder()
    uploaded_problem_zip.seek(0)
    with zipfile.ZipFile(uploaded_problem_zip, "r") as zip_ref:
        zip_ref.extractall(tmp_folder)
    
    pdf_path = str(Path(tmp_folder) / "dom" / "problem.pdf")
    # from statement.tex get problem description text
    with open(str(Path(tmp_folder) / "statement.tex"), "r", encoding="utf-8") as f:
        problem_description = []
        for line in f.readlines():
            if line[0] == "%": continue
            problem_description.append(line)

    st.session_state["problem_pdf"] = pdf_path
    st.session_state["file_name"] = file_name
    st.session_state["problem_description"] = "\n\n".join(problem_description)
    save_problem_id(problem_id)
    
    st.info(f"{file_name}.zip 上傳成功")
    
def save_problem_id(problem_id):
    st.session_state["problem_id"] = problem_id

add_page_title()

# **can't get problem_pdf and problem_description**
# selected_problem_id = st.selectbox(
#     label="題目列表", 
#     placeholder="選擇已儲存的題目", 
#     options=list(map(lambda x:x.name, exist_problems)), 
#     index=None
# )
# st.button("確定", on_click=save_problem_id, args=(selected_problem_id, ))

st.write("## 上傳題目")
uploaded_problem_id = st.text_input("題目代號")
uploaded_problem_zip = st.file_uploader("開啟題目 .zip 檔案", type="zip")
submit_btn = st.button("上傳", on_click=save_file, args=(uploaded_problem_id, uploaded_problem_zip))
st.markdown("""
壓縮檔目錄與必要檔案
- file_name.zip
    - dom/
        - data/  <-- 測試資料
        - problem.pdf  <-- 題目預覽
    - statement.tex  <-- 詢問時的題目敘述
""")