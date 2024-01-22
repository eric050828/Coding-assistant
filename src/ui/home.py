import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title
from utils.vectorDB import *
from utils.file import *


show_pages(
    [
        Page("src/ui/home.py", "首頁", "👋"),
        Section("競賽"),
        Page("src/ui/select_problem.py", "選擇題目", in_section=True),
        Page("src/ui/problem_preview.py", "題目預覽", in_section=True),

        Section("資料庫"),
        Page("src/ui/code_list.py", "檢視程式碼", in_section=True),
        Page("src/ui/add_codes.py", "新增程式碼", in_section=True),
        Page("src/ui/delete_codes.py", "刪除程式碼", in_section=True),
        # Page("src/ui/search_codes.py", "尋找程式碼", in_section=True),

        Section("程式助手"),
        Page("src/ui/editor.py", "編輯器", in_section=True),
        Page("src/ui/edit_testcase.py", "編輯測資", in_section=True),
        Page("src/ui/verify_testcase.py", "驗證測資", in_section=True),
    ]
)

add_page_title()

def clear_state():
    remove_tmp_folder()
    st.session_state.clear()


st.sidebar.button("清除暫存資料", on_click=clear_state, type="primary")

st.write("## 已儲存的題目")
exist_problems = get_exist_problems()
exist_problems = list(map(lambda x:x.name, exist_problems))
problem_codes_count = [len(show_codes_data(name)) for name in exist_problems]
st.dataframe(
    {
        "題目代號": exist_problems,
        "程式碼數量": problem_codes_count,
    },
    hide_index=True,
    use_container_width=True
)
st.bar_chart(
    dict(zip(exist_problems, problem_codes_count))
)