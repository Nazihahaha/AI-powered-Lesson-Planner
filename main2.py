import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
import io

load_dotenv()

def LLM_Setup(prompt, file_content=None):
    model = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv('key')
    )
    parser = StrOutputParser()
    if file_content:
        # Append file content to the prompt if available
        prompt = f"{prompt}\n\nUse the following file content to inform the lesson plan:\n{file_content}"
    output = (parser | model).invoke(prompt)
    # Extract text content from AIMessage and clean it
    output_text = output.content if hasattr(output, 'content') else str(output)
    output_text = output_text.replace('n*', '').replace('n#####', '')
    return output_text

st.title('AI Lesson Planner')

subject = st.text_input(label='Subject')
topic = st.text_input(label='Topic')
grade = st.text_input(label='Grade')
duration = st.text_input(label='Duration')
learning_objectives = st.text_area(label='Learning Objective')
customization = st.text_area(label='Customization')

# File uploader
uploaded_file = st.file_uploader("Upload a file (e.g., PDF, text, or image) to inform the lesson plan", type=["pdf", "txt", "png", "jpg", "jpeg"])

file_content = None
if uploaded_file is not None:
    # Read file content based on file type
    if uploaded_file.type == "application/pdf":
        from PyPDF2 import PdfReader
        pdf_reader = PdfReader(uploaded_file)
        file_content = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
    elif uploaded_file.type in ["text/plain", "image/png", "image/jpeg", "image/jpg"]:
        file_content = uploaded_file.read().decode("utf-8") if uploaded_file.type == "text/plain" else f"Image file uploaded: {uploaded_file.name}"
    else:
        st.warning("Unsupported file type. Please upload a PDF, text, or image file.")
        file_content = None

if st.button('Generate Lesson Plan'):
    if not subject or not topic or not grade or not duration or not learning_objectives:
        st.warning('Please fill out all required fields before generating the lesson plan.')
    else:
        prompt = (
            f"Generate a detailed lesson plan for the subject of {subject} on the topic of {topic}. "
            f"This lesson is intended for {grade} students and will last for {duration}. "
            f"The following are the learning objectives: {learning_objectives}. "
            f"Return the results as well-structured Markdown, including sections for Introduction, Learning Objectives, Materials, Activities, and Conclusion. "
            f"Do not include class size. Customize the plan to be {customization}."
        )
        llm_output = LLM_Setup(prompt, file_content)
        st.markdown(llm_output)
