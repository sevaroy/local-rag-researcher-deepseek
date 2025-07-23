import pyperclip
import streamlit as st
import streamlit_nested_layout
from src.assistant.graph import researcher
from src.assistant.utils import get_report_structures, process_uploaded_files
from dotenv import load_dotenv

load_dotenv()

def generate_response(user_input, enable_web_search, report_structure, max_search_queries):
    """
    Generate response using the researcher agent and stream steps
    """
    # Initialize state for the researcher
    initial_state = {
        "user_instructions": user_input,
    }
    
    # Langgraph researcher config
    config = {"configurable": {
        "enable_web_search": enable_web_search,
        "report_structure": report_structure,
        "max_search_queries": max_search_queries,
    }}

    # Create the status for the global "Researcher" process
    langgraph_status = st.status("**研究員正在運行...**", state="running")

    # Force order of expanders by creating them before iteration
    with langgraph_status:
        generate_queries_expander = st.expander("生成研究查詢", expanded=False)
        search_queries_expander = st.expander("搜索查詢", expanded=True)
        final_answer_expander = st.expander("生成最終答案", expanded=False)

        steps = []

        # Run the researcher graph and stream outputs
        for output in researcher.stream(initial_state, config=config):
            for key, value in output.items():
                expander_label = key.replace("_", " ").title()

                if key == "generate_research_queries":
                    with generate_queries_expander:
                        st.write(value)

                elif key.startswith("search_and_summarize_query"):
                    with search_queries_expander:
                        with st.expander(expander_label, expanded=False):
                            st.write(value)

                elif key == "generate_final_answer":
                    with final_answer_expander:
                        st.write(value)

                steps.append({"step": key, "content": value})

    # Update status to complete
    langgraph_status.update(state="complete", label="**使用 Langgraph** (研究已完成)")

    # Return the final report
    return steps[-1]["content"] if steps else "No response generated"

def clear_chat():
    st.session_state.messages = []
    st.session_state.processing_complete = False
    st.session_state.uploader_key = 0

def main():
    st.set_page_config(page_title="DeepSeek RAG 研究助手", layout="wide")

    # Initialize session states
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_report_structure" not in st.session_state:
        st.session_state.selected_report_structure = None
    if "max_search_queries" not in st.session_state:
        st.session_state.max_search_queries = 5  # Default value of 5
    if "files_ready" not in st.session_state:
        st.session_state.files_ready = False  # Tracks if files are uploaded but not processed

    # Title row with clear button
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("📄 DeepSeek R1 RAG 研究助手")
    with col2:
        if st.button("清除對話", use_container_width=True):
            clear_chat()
            st.rerun()

    # Sidebar configuration
    st.sidebar.title("研究設置")

    # Add report structure selector to sidebar
    report_structures = get_report_structures()
    default_report = "standard report"

    selected_structure = st.sidebar.selectbox(
        "選擇報告結構",
        options=list(report_structures.keys()),
        index=list(map(str.lower, report_structures.keys())).index(default_report)
    )

    st.session_state.selected_report_structure = report_structures[selected_structure]

    # Maximum search queries input
    st.session_state.max_search_queries = st.sidebar.number_input(
        "最大搜索查詢數量",
        min_value=1,
        max_value=10,
        value=st.session_state.max_search_queries,
        help="設置要進行的最大搜索查詢數量。(1-10)"
    )
    
    enable_web_search = st.sidebar.checkbox("啟用網絡搜索", value=False)

    # Upload file logic
    uploaded_files = st.sidebar.file_uploader(
        "上傳新文檔",
        type=["pdf", "txt", "csv", "md"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}"
    )

    # Check if files are uploaded but not yet processed
    if uploaded_files:
        st.session_state.files_ready = True  # Mark that files are available
        st.session_state.processing_complete = False  # Reset processing status

    # Display the "Process Files" button **only if files are uploaded but not processed**
    if st.session_state.files_ready and not st.session_state.processing_complete:
        process_button_placeholder = st.sidebar.empty()  # Placeholder for dynamic updates

        with process_button_placeholder.container():
            process_clicked = st.button("處理文件", use_container_width=True)

        if process_clicked:
            with process_button_placeholder:
                with st.status("正在處理文件...", expanded=False) as status:
                    # Process files (Replace this with your actual function)
                    if process_uploaded_files(uploaded_files):
                        st.session_state.processing_complete = True
                        st.session_state.files_ready = False  # Reset files ready flag
                        st.session_state.uploader_key += 1  # Reset uploader to allow new uploads

                    status.update(label="文件處理成功！", state="complete", expanded=False)
                    # st.rerun()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])  # Show the message normally

            # Show copy button only for AI messages at the bottom
            if message["role"] == "assistant":
                if st.button("📋", key=f"copy_{len(st.session_state.messages)}"):
                    pyperclip.copy(message["content"])

    # Chat input and response handling
    if user_input := st.chat_input("在此輸入您的問題..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Generate and display assistant response
        report_structure = st.session_state.selected_report_structure["content"]
        assistant_response = generate_response(
            user_input, 
            enable_web_search, 
            report_structure,
            st.session_state.max_search_queries
        )

        # Store assistant message
        st.session_state.messages.append({"role": "assistant", "content": assistant_response["final_answer"]})

        with st.chat_message("assistant"):
            st.write(assistant_response["final_answer"])  # AI response

            # Copy button below the AI message
            if st.button("📋", key=f"copy_{len(st.session_state.messages)}"):
                pyperclip.copy(assistant_response["final_answer"])

if __name__ == "__main__":
    main()