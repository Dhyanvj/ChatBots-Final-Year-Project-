import streamlit as st
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template

import openai
import fitz # PyMuPDF
import os

# Load environment variables from .env
load_dotenv()

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        doc = fitz.open(stream=pdf.read(), filetype="pdf")
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)

def summarize_pdf_content(raw_text, max_sentences=3):
    response = openai.Completion.create(  # Use the correct endpoint
        engine="gpt-3.5-turbo-instruct",  # Specify the engine
        prompt=f"Summarize this PDF content:\n{raw_text}",  # Provide a clear prompt
        max_tokens=150 * max_sentences,
        n=max_sentences,
        stop=None,  # Allow for longer summaries if needed
        temperature=0.7  # Encourage creativity and variety
    )

    summary = response.choices[0].text.strip()  # Extract the summary from the response
    return summary

def generate_example_questions(raw_text, num_questions=5):
    response = openai.Completion.create(  # Use the correct endpoint
        engine="gpt-3.5-turbo-instruct",  # Specify the engine
        prompt=f"Generate {num_questions} example questions based on this text:\n{raw_text}",  # Provide a clear prompt
        max_tokens=150 * num_questions,  # Set max tokens for concise questions
        n=1,  # Generate only 1 response (containing multiple questions)
        stop=None,  # Allow for longer questions if needed
        temperature=0.9  # Encourage more diverse and challenging questions
    )

    # Extract the questions as a single string, preserving newlines
    questions_string = response.choices[0].text.strip()  # Keep newlines for separation

    return questions_string

def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    raw_text = ""

    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):

                raw_text = get_pdf_text(pdf_docs)

                text_chunks = get_text_chunks(raw_text)

                vectorstore = get_vectorstore(text_chunks)

                st.session_state.conversation = get_conversation_chain(
                    vectorstore)

    with st.expander("PDF Content"):
        if raw_text:
            pdf_content = raw_text
            st.write(pdf_content)
        else:
            st.write("No PDF content available.")

    with st.expander("Summary of PDF Content"):
        if raw_text:
            pdf_summary = summarize_pdf_content(raw_text)
            st.write(pdf_summary)
        else:
            st.write("No PDF content available for summarization.")

    with st.expander("Example Questions"):
        if "conversation" in st.session_state and st.session_state.conversation is not None:
            st.subheader("Example Questions Based on PDF Content:")
            example_questions = generate_example_questions(raw_text)
            st.write(example_questions)

if __name__ == '__main__':
    main()
