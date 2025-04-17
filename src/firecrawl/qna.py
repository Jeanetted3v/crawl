"""To run:
python -m src.firecrawl.qna
"""
import os
import gradio as gr
from langchain_experimental.text_splitter import SemanticChunker
from langchain.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name="gpt-4.1-mini",
    temperature=0.1
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer",
)

chunks = None
qa_chain = None
source_documents = []

def load_documents():
    with open("./data/firecrawl/translated_info.txt", "r", encoding="utf-8") as f:
        content = f.read()
    text_splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",  # Default method
        breakpoint_threshold_amount=95.0,  # Default is 95.0 - adjust based on your content
        min_chunk_size=100  # Minimum size for chunks in characters
    )
    chunks = text_splitter.split_text(content)
    return chunks

def initialize_qa():
    global chunks, qa_chain
    chunks = load_documents()
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name="company_info"
    )
    
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True
    )
    
    return f"Ready! Loaded {len(chunks)} semantic chunks from the company information."

def process_query(message, history):
    global qa_chain, source_documents
    
    if qa_chain is None:
        init_message = initialize_qa()
        return [[message, init_message]]
    response = qa_chain({"question": message})
    source_documents = response.get("source_documents", [])
    history.append([message, response["answer"]])
    return history

def get_sources():
    sources_text = ""
    for i, doc in enumerate(source_documents):
        sources_text += f"Source {i+1}:\n{doc.page_content}\n\n"
    
    return sources_text if sources_text else "No sources available"

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Company Information Q&A")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="Ask a question about the company")
            submit_btn = gr.Button("Submit")
        
        with gr.Column(scale=2):
            sources_display = gr.Textbox(label="Sources", lines=15)
            refresh_sources = gr.Button("Show Sources")
    
    # Initialize on page load
    demo.load(lambda: initialize_qa())
    
    # Handle user input
    submit_btn.click(
        process_query,
        inputs=[msg, chatbot],
        outputs=chatbot
    ).then(
        lambda: "",
        outputs=msg
    )
    
    # Show sources when requested
    refresh_sources.click(
        get_sources,
        outputs=sources_display
    )


if __name__ == "__main__":
    demo.launch()