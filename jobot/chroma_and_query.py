import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import pandas as pd

df = pd.read_csv("/home/san/Desktop/jobot/data/processed/processed_jobfile.csv")
df["job_text"] = df["job_title"] + " " + df["job_category"] + " " + df["professional_skill_required"]

# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path="/home/san/Desktop/joBot_src/data/chroma")  # Stores vectors persistently
# Create the collection (if it doesn't exist)
collection = chroma_client.get_or_create_collection("job_embeddings")  # Collection name

# Load Sentence Transformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# flag embeddings herne, snowflakes

# Generate embeddings and store them in ChromaDB
for index, row in df.iterrows():
    text = row["job_text"]
    if isinstance(text, str):  # Only encode valid strings
        embedding = model.encode(text).tolist()
        collection.add(ids=[str(index)], embeddings=[embedding], metadatas=[row.to_dict()])




# User's query
user_query = "Good Morning"

# Format the retrieved job data for context
context = """
- Software Engineer requiring Python, Django, and FastAPI.
- Data Analyst requiring Python and SQL.
- Backend Developer requiring Python and Flask.
"""

# Prepare the prompt
prompt = (
    f"Based on the following job details:\n{context}\n\n"
    f"Answer the user's query: {user_query}"
)

# Generate response using LLaMA 2
response = ollama.chat(
    model='llama2',
    messages=[{'role': 'user', 'content': prompt}]
)

print(response)

