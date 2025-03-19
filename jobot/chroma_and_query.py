import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import pandas as pd

# Load the job data
df = pd.read_csv("/home/san/Desktop/jobot/data/processed/processed_jobfile.csv")
df["job_text"] = (
    df["job_title"] + " " +
    df["job_category"] + " " +
    df["professional_skill_required"] + " " +
    df["job_location"] + " " +
    df["offered_salary"]+ " " +
    df["deadline"]
)


# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path="/home/san/Desktop/jobot/data/chroma")
collection = chroma_client.get_or_create_collection("job_embeddings")

# Load Sentence Transformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Check if embeddings already exist in the collection
existing_ids = set(collection.get()["ids"])  # Get all existing IDs in the collection

# Generate and store embeddings only for new rows
new_embeddings_added = False
for index, row in df.iterrows():
    text = row["job_text"]
    if isinstance(text, str):  # Only encode valid strings
        embedding_id = str(index)
        if embedding_id not in existing_ids:  # Only add if the ID doesn't exist
            embedding = model.encode(text).tolist()
            collection.add(ids=[embedding_id], embeddings=[embedding], metadatas=[row.to_dict()])
            new_embeddings_added = True

if new_embeddings_added:
    print("New embeddings added successfully!")
else:
    print("No new embeddings to add. Using existing embeddings.")

# User's query
user_query = "GoodMorning, I am looking for python jobs in or around kathmandu,nepal"

# Generate embedding for the user's query
query_embedding = model.encode(user_query).tolist()

# Query ChromaDB for the most similar jobs
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=6 # Retrieve top 6 most similar jobs
)

# Format the retrieved job data for context
context = ""
for metadata in results["metadatas"][0]:  # Access metadata of the top results
    context += f"- {metadata['job_title']} requiring {metadata['professional_skill_required']}.\n"

# Prepare the prompt
prompt = (
    "You are a helpful career assistant. Your task is to provide job recommendations based on the following job details:\n"
    f"{context}\n\n"
    f"User Query: {user_query}\n\n"
    "Instructions:\n"
    "1. Analyze the user's query and match it with the most relevant jobs from the provided list.\n"
    "2. Provide a concise and clear response, listing the top 3 most relevant jobs.\n"
    "3. For each job, include the job title and required skills.\n"
    "4. If no relevant jobs are found, politely inform the user.\n\n"
    "5. Provide Salary And deadline Information if available as well.\n\n"
    "Example Response:\n"
    "Here are some job opportunities that match your query:\n"
    "- Software Engineer: Requires Python, Django, and FastAPI.\n"
    "- Data Analyst: Requires Python and SQL.\n"
    "- Backend Developer: Requires Python and Flask.\n\n"
    "Now, respond to the user's query:"
)

# Generate response using LLaMA 2
response = ollama.chat(
    model='llama2',
    messages=[{'role': 'user', 'content': prompt}]
)

print(response['message']['content'])