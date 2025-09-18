Overview:

The MA_DIGITAL_CHATBOT is a web-based chatbot application designed to answer queries about MA Digital's products, services, and company information using data scraped from their website. Built with a FastAPI backend and a JavaScript/HTML frontend, it leverages a retrieval-augmented generation (RAG) pipeline with FAISS for vector search and OpenAI’s GPT-4o-mini for natural language processing. This document outlines the step-by-step process of building the project and identifies unnecessary code with suggested improvements.
Step-by-Step Development Process
1. Project Setup and Environment Configuration

Objective: Establish the project structure and environment.
Actions:
Created MA_DIGITAL_CHATBOT directory with a .venv for dependency isolation.
Configured pyproject.toml and uv.lock for dependency management (e.g., fastapi, langchain, requests).
Set up .env for environment variables (e.g., OPENAI_API_KEY) using utils.py’s load_env().


Files:
.env: Stores sensitive variables.
pyproject.toml, uv.lock: Manage dependencies.
utils.py: Utility functions for environment and file operations.



2. Data Scraping

Objective: Collect content from https://madigitalhub.com/ for the chatbot's knowledge base.
Actions:
Developed run_scraper.py to crawl the website using requests and BeautifulSoup.
Implemented clean_text_with_links() to remove non-content tags and augment links (e.g., WhatsApp, email).
Filtered valid URLs with is_valid_url() and saved data to backend/data/scraped_data.json.


Files:
run_scraper.py: Scraping logic.
backend/data/scraped_data.json: Scraped content.
utils.py: JSON file handling.



3. RAG Pipeline Creation

Objective: Build a vector store for efficient content retrieval.
Actions:
Created rag_pipeline.py to process scraped_data.json into a FAISS vector store.
Split content into chunks using RecursiveCharacterTextSplitter (1000 characters, 200 overlap).
Embedded chunks with OpenAIEmbeddings and saved the index to backend/data/faiss_index.


Files:
rag_pipeline.py: Vector store creation and loading.
run_embedd.py: Executes vector store creation.
backend/data/faiss_index: Stores FAISS index files.



4. Query Engine Development

Objective: Process user queries with RAG and generate responses.
Actions:
Built query_engine.py using LangChain’s RetrievalQA with a FAISS retriever (k=3).
Defined a detailed PromptTemplate to ensure context-based, formatted responses.
Implemented get_bot_response() (non-streaming) and get_bot_response_stream() (streaming) with markdown formatting.
Added CLI testing with a dummy vector store for development.


Files:
query_engine.py: Query processing logic.
rag_pipeline.py: Vector store support.



5. FastAPI Backend

Objective: Create an API to handle chat requests and serve the frontend.
Actions:
Developed main.py with FastAPI, mounting static for file serving and enabling CORS.
Defined endpoints: / (status), /widget (serves widget.html), /chat (streaming), /chat-sync (non-streaming).
Used Pydantic models for request/response validation.


Files:
main.py: FastAPI application.
query_engine.py: Response generation functions.



6. Frontend Chat Widget

Objective: Build a user-friendly chat interface.
Actions:
Created index.html as a test page to embed the widget via embed.js.
Developed widget.html with CSS for styling and JavaScript for streaming responses, using marked.js for markdown.
Implemented embed.js to create a floating widget with a toggle button and iframe.


Files:
frontend/index.html: Test page.
static/js/widget.html: Chat widget interface.
static/js/embed.js: Widget embedding logic.



7. Testing and Deployment

Objective: Validate functionality and prepare for deployment.
Actions:
Ran run_scraper.py and run_embedd.py to generate data and vector store.
Started the FastAPI server with uvicorn main:app --reload.
Tested the widget at http://localhost:8000/frontend/index.html.
Used CLI in query_engine.py for query testing.


Files:
run_scraper.py, run_embedd.py, main.py: Core scripts.
query_engine.py: CLI testing.
 
Ensure marked.js reliability with a backup CDN in widget.html.



Conclusion
The MA_DIGITAL_CHATBOT was built with a robust backend (FastAPI, RAG with FAISS) and a dynamic frontend (chat widget with streaming), ensuring a professional chatbot for MA Digital. 