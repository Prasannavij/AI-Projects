import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Agent Harness Scraper", layout="centered", page_icon="🤖")

st.markdown("""
    <style>
    .main {background-color: #0E1117;}
    h1 {color: #FF4B4B;}
    .stTextInput input {border-radius: 10px;}
    .stButton button {background-color: #FF4B4B; color: white; border-radius: 10px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Web Agent Analyzer")
st.markdown("Enter any public URL below. The local AI Agent will spin up Playwright in the background, harvest the website data, and summarize it for you!")

# Input form
url_input = st.text_input("🔗 Target URL", placeholder="https://en.wikipedia.org/wiki/Artificial_intelligence")

# We manage state so downloading files doesn't reset the app!
if "task_completed" not in st.session_state:
    st.session_state.task_completed = False

if st.button("🚀 Deploy Agent"):
    if url_input:
        # Reset state at the start of a new run
        st.session_state.task_completed = False
        with st.spinner(f"Agent '{url_input}' is launching (Watch your Terminal for live logs!)..."):
            
            parent_dir = os.path.dirname(os.getcwd())
            
            # Use 'capture_output=False' so the live Agent logs pipe seamlessly to your physical terminal!
            subprocess.run(
                ["uv", "run", "python", "run_task.py", url_input], 
                capture_output=False, 
                cwd=parent_dir
            )
            
            st.session_state.task_completed = True
    else:
        st.warning("Please type a valid URL first!")

# Display the results strictly from State so it persists across download button clicks!
if st.session_state.task_completed:
    parent_dir = os.path.dirname(os.getcwd())
    details_path = os.path.join(parent_dir, "outputs", "details.json")
    summary_path = os.path.join(parent_dir, "outputs", "summary.txt")
    
    if os.path.exists(details_path) and os.path.exists(summary_path):
        st.success("✅ Agent Completed Task successfully!")
        
        # Show summary explicitly
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_content = f.read()
        
        st.subheader("Agent Output:")
        st.code(summary_content, language="markdown")
        
        # Download Buttons side by side
        col1, col2 = st.columns(2)
        with col1:
            with open(details_path, "r", encoding="utf-8") as f:
                st.download_button(
                    label="📥 Download Raw Agent Data (JSON)",
                    data=f.read(),
                    file_name="extraction_details.json",
                    mime="application/json"
                )
        with col2:
            st.download_button(
                label="📥 Download Summary File (TXT)",
                data=summary_content,
                file_name="site_summary.txt",
                mime="text/plain"
            )
    else:
        st.error("The agent crashed or failed to generate the outputs. Please check your terminal.")
