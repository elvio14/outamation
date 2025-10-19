# Load environment variables from a .env file (located in the current working directory)
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "api_key")

from llama_index.core import SimpleDirectoryReader

# Load PDF or text document
documents = SimpleDirectoryReader("sample_docs").load_data()
print(f"Loaded {len(documents)} documents.")

from llama_index.core.node_parser import SentenceSplitter

splitter_fixed = SentenceSplitter(chunk_size=300, chunk_overlap=0)  # No overlap
chunks_fixed = splitter_fixed.get_nodes_from_documents(documents)
print(f"Total Fixed-Length Chunks Created: {len(chunks_fixed)}")

splitter_overlap = SentenceSplitter(chunk_size=300, chunk_overlap=50)  # 50-token overlap
chunks_overlap = splitter_overlap.get_nodes_from_documents(documents)
print(f"Total Overlapping Chunks Created: {len(chunks_overlap)}")

# from llama_index.core.node_parser import SemanticSplitter

# semantic_splitter = SemanticSplitter()
# chunks_semantic = semantic_splitter.get_nodes_from_documents(documents)
# print(f"Total Semantic Chunks Created: {len(chunks_semantic)}")

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load embedding model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Apply embeddings
for chunk in chunks_overlap:  # Using Overlapping Chunks for best retrieval
    chunk.embedding = embed_model.get_text_embedding(chunk.text)

print("Embeddings Generated Successfully!")

from llama_index.core import VectorStoreIndex

# Create an index with our embeddings
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

from llama_index.llms.gemini import Gemini

# Initialize Gemini LLM - use a supported model name (remove the "models/" prefix)
# If "gemini-1.5" is not available for your account, replace it with a model name that is.
llm = Gemini(model="gemini-2.5-flash", api_key=GOOGLE_API_KEY)

# Set up query engine with our custom components
query_engine = index.as_query_engine(
    llm=llm,
    similarity_top_k=2  # Retrieve top 2 most similar chunks
)

# Test a retrieval query
response = query_engine.query("What is the document about?")
print(response) 