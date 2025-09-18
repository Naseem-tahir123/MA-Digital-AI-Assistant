

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from rag_pipeline import load_vector_store
import openai
import html

# Load vector store and set up retriever
vector_store = load_vector_store()
if vector_store is None:
    raise ValueError("Failed to load vector store. Please check rag_pipeline.py")
retriever = vector_store.as_retriever(search_type="similarity", k=3)

# Detailed prompt template
detailed_prompt_template_str = """
You are "MA Digital Bot", the official AI assistant for MA Digital. Your primary purpose is to assist users by accurately answering their questions about MA Digital's products, services, company information, pricing, technical specifications, solutions, case studies, career opportunities, contact information, and any other information found on the MA Digital website.

You will be provided with:
1.  The user's question.
2.  Relevant excerpts (context) scraped from the MA Digital website.

**Your Instructions:**

1.  **Base Your Answer STRICTLY on the Provided Context:** Your answers MUST be derived SOLELY from the information within the provided context. Do not use any prior knowledge or information outside of this context.
2.  **Acknowledge if Information is Missing:** If the provided context does not contain the information needed to answer the question, you MUST explicitly state that the information is not available in the provided documents or that you cannot find the specific detail based on the website data. Do NOT invent, infer, or hallucinate answers.
3.  **Be Specific and Cite (Implicitly):** When answering, directly address the user's query using the information from the context. You don't need to say "According to the context...", but your answer should clearly reflect that it's based on the provided information.
4.  **Maintain a Professional and Helpful Tone:** Your responses should be polite, clear, concise, and professional, reflecting MA Digital's brand. **Structure your responses for easy readability, using paragraphs for distinct points and well-formatted lists as detailed below.**
5.  **Handle Ambiguity:** If the user's question is ambiguous or lacks detail, you can ask a polite clarifying question. However, first attempt to answer based on the most likely interpretation given the context.
6.  **Keep it Focused:** Only answer the question asked. Do not provide unsolicited information unless it's directly and highly relevant to clarifying the answer from the context.
7.  **No External Links or Recommendations (unless in context):** Do not suggest external websites or resources unless they are explicitly mentioned in the provided context from the MA Digital website.
8.  **Summarize if Necessary:** If the context contains a lot of relevant information, summarize it concisely to answer the user's question.
9.  **Direct Quotes (Sparingly):** You can use short, direct quotes from the context if they perfectly answer the question, but prefer to synthesize the information into your own words.
10. **Safety:** Do not answer questions that are off-topic, offensive, unethical, or request an opinion rather than factual information from the website. If asked for an opinion, state that you can only provide information found on the MA Digital website.
11. **To-the-Point Answers for Specific Data:** When asked for a specific piece of information like a phone number, email, or WhatsApp number, provide it directly and concisely.
12. **Enhanced List Formatting for Readability (CRITICAL):**
    When presenting information as a list (e.g., services, features), follow these rules precisely:
    *   If there's an introductory sentence for the list, place it before the list begins, followed by a single newline.
    *   Use standard numbered lists (e.g., `1.`, `2.`).
    *   **For EACH item in a numbered list:**
        *   The item number (e.g., `1.`) can be on the same line as the bolded title OR the bolded title can start on the line immediately after the item number.
        *   The **title/heading** of the item (e.g., "Development Services") MUST be **bolded using markdown** (e.g., `**Development Services**`).
        *   **CRITICAL:** There MUST be a **newline character (`\\n`)** immediately AFTER the closing `**` of the bolded title.
        *   The **description** for that item MUST start on the line immediately following the bolded title (i.e., after the newline character).

**User's Question:**
{question}

**Retrieved Context from MA Digital Website:**
{context}

**MA Digital Bot's Answer:**
"""

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=detailed_prompt_template_str
)

# Load LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Create the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt_template},
    return_source_documents=True,
)

# Initialize OpenAI client
client = openai.OpenAI()

# Non-streaming version (fallback)
def get_bot_response(query: str) -> str:
    result_dict = qa_chain.invoke({"query": query})
    response_text = result_dict.get("result", "Sorry, I couldn't process your request.")
    
    # Unescape HTML characters
    unescaped_response = html.unescape(response_text)
    
    # Ensure proper markdown formatting for lists
    formatted_response = unescaped_response.replace('**\n', '**\n\n')
    
    return formatted_response.strip()

# Corrected streaming version
def get_bot_response_stream(query: str):
    try:
        # Retrieve documents using the correct method
        docs = retriever.get_relevant_documents(query)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Format the prompt
        prompt = prompt_template.format(context=context, question=query)
        
        # Create the messages
        messages = [{"role": "user", "content": prompt}]
        
        # Create streaming response
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
            temperature=0,
        )
        
        buffer = ""
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                token = chunk.choices[0].delta.content
                buffer += token
                
                # Send tokens when we have complete words or formatting
                if token.endswith((' ', '\n', '.', ',', '!', '?', ':', ';', ')', ']', '}', '*')):
                    # Process the buffer
                    processed_content = html.unescape(buffer)
                    formatted_content = processed_content.replace('**\n', '**\n\n')
                    yield formatted_content
                    buffer = ""
                elif len(buffer) > 50:  # Send long buffers to avoid delays
                    processed_content = html.unescape(buffer)
                    formatted_content = processed_content.replace('**\n', '**\n\n')
                    yield formatted_content
                    buffer = ""
        
        # Send any remaining content
        if buffer:
            processed_content = html.unescape(buffer)
            formatted_content = processed_content.replace('**\n', '**\n\n')
            yield formatted_content
                
    except Exception as e:
        yield f"Error: {str(e)}"

# CLI testing code
if __name__ == "__main__":
    print("MA Digital Bot is ready. Type 'exit' to quit.")
    
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain.docstore.document import Document

    if vector_store is None:
        print("Using dummy vector store for testing list formatting.")
        dummy_texts = [
            "MA Digital offers several key services. Web Development involves skilled developers creating custom websites and applications. Social Media Marketing focuses on growing audience engagement and brand presence. SEO Services help websites rank higher on search engines. Graphics & Multimedia provides engaging videos, graphics, and interactive content.",
            "Regarding our service portfolio: For Development, we have experts in coding and team assembly. For Design, our designers enhance project look and feel. Operations include cloud setup and quality control. DevOps ensures efficient code integration."
        ]
        dummy_documents = [Document(page_content=text) for text in dummy_texts]
        dummy_embeddings = OpenAIEmbeddings()
        try:
            vector_store = FAISS.from_documents(dummy_documents, dummy_embeddings)
            retriever = vector_store.as_retriever(search_type="similarity", k=1)
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=retriever,
                chain_type="stuff",
                chain_type_kwargs={"prompt": prompt_template},
                return_source_documents=True,
            )
        except Exception as e:
            print(f"Could not create dummy vector store: {e}. Ensure OPENAI_API_KEY is set.")
            exit()

    while True:
        user_input = input("Ask MA Digital Assistant: ")
        if user_input.lower() == 'exit':
            break
        if user_input:
            print("MA Digital Assistant:")
            # Test streaming
            for token in get_bot_response_stream(user_input):
                print(token, end='', flush=True)
            print("\n")
        else:
            print("Please ask a question.")