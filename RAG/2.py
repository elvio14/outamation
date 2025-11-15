import fitz  # PyMuPDF

# Load PDF document
doc = fitz.open("sample_docs/sample_contract.pdf")

# Extract text from all pages
text = "\n".join([page.get_text() for page in doc])

print(f"Extracted {len(text.split())} words from the PDF.")

from llama_index.llms.gemini import Gemini
from llama_index.core.llms import ChatMessage

# Set up Gemini API key
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "api_key")

# Initialize Gemini LLM
llm = Gemini(model="gemini-2.5-flash", api_key=GOOGLE_API_KEY)

# Define query rewriting function
def rewrite_query(user_query):
    messages = [
        ChatMessage(role="system", content="Rewrite this query for improved retrieval relevance."),
        ChatMessage(role="user", content=user_query),
    ]
    response = llm.chat(messages)
    return response.message.content

# Test query rewriting
query = "What are the penalties for late payments?"
expanded_query = rewrite_query(query)

print(f"Original Query: {query}")
print(f"Expanded Query: {expanded_query}")

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

# Load documents from the directory
documents = SimpleDirectoryReader("sample_docs").load_data()

# Initialize Hugging Face embedding model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create a document store
docstore = SimpleDocumentStore()

# Create a vector index for embedding-based retrieval
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
vector_retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=5)

# Set up query engine with Gemini LLM and retriever
query_engine = RetrieverQueryEngine(
    retriever=vector_retriever,
    llm=llm  # This tells the query engine to use Gemini for generating responses
)

# Alternative approach: Use the vector index query engine directly with Gemini LLM
# This is often simpler and more effective
vector_query_engine = vector_index.as_query_engine(llm=llm, similarity_top_k=5)

# Test both approaches
print("=== Using RetrieverQueryEngine ===")
query = "What is the total estimated monthly payment?"
response = query_engine.query(query)
print(response)

print("\n=== Using VectorIndex Query Engine ===")
response_vector = vector_query_engine.query(query)
print(response_vector)

print("\n=== Second Query ===")
query2 = "How much does the borrower pay for lender's title insurance?"
response2 = query_engine.query(query2)
print(response2)

response2_vector = vector_query_engine.query(query2)
print(f"\nVector Engine Response: {response2_vector}")

# Optional: You can also use query rewriting with the query engine
print("\n=== Using Query Rewriting + RAG ===")
expanded_query = rewrite_query(query)
print(f"Expanded Query: {expanded_query}")
response_expanded = vector_query_engine.query(expanded_query)
print(f"Response with expanded query: {response_expanded}")