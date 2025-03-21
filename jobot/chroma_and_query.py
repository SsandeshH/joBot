from flask import Flask, request, jsonify, render_template
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import ollama
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize

nltk.download('punkt')

app = Flask(__name__)

# Load and clean job data
try:
    df = pd.read_csv("/home/san/Desktop/jobot/data/processed/processed_jobfile.csv")
    df.fillna("Not Specified", inplace=True)
    expected_columns = [
        "job_title", 
        "job_category", 
        "professional_skill_required", 
        "job_location", 
        "offered_salary", 
        "deadline"
    ]
    for col in expected_columns:
        if col not in df.columns:
            raise ValueError(f"Missing expected column: {col}")
except Exception as e:
    app.logger.error(f"Error loading CSV: {e}")
    raise

# Create a combined job text for BM25 scoring
df["job_text"] = (
    df["job_title"].str.lower() + " " +
    df["job_category"].str.lower() + " " +
    df["professional_skill_required"].str.lower() + " " +
    df["job_location"].str.lower() + " " +
    df["offered_salary"].str.lower() + " " +
    df["deadline"].str.lower()
)

# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path="/home/san/Desktop/jobot/data/chroma")
collection = chroma_client.get_or_create_collection("job_embeddings")

# Load Sentence Transformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# BM25 Preparation using tokenized job_text
tokenized_corpus = [word_tokenize(text) for text in df["job_text"].tolist()]
bm25 = BM25Okapi(tokenized_corpus)

# Simple Intent Classifier to detect job-related queries
def is_job_related(query):
    job_keywords = ['job', 'developer', 'engineer', 'hiring', 'position', 'vacancy', 'role']
    return any(keyword in query.lower() for keyword in job_keywords)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    user_query = request.form['inp-field'].strip().lower()

    if is_job_related(user_query):
        # BM25 Scoring
        tokenized_query = word_tokenize(user_query)
        bm25_scores = bm25.get_scores(tokenized_query)

        # Extract top BM25 results (top 10)
        top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:10]
        bm25_jobs = df.iloc[top_bm25_indices]

        # For general job recommendations, use all BM25 jobs without additional filtering
        filtered_bm25_jobs = bm25_jobs

        # ChromaDB Search using the Sentence Transformer embedding
        query_embedding = model.encode(user_query).tolist()
        results = collection.query(query_embeddings=[query_embedding], n_results=10)

        # Extract all results from ChromaDB without filtering by specific skills
        chroma_jobs = [
            (metadata["job_title"], score)
            for metadata, score in zip(results["metadatas"][0], results["distances"][0])
        ]

        # Combine scores from both BM25 and ChromaDB (adjust weights if needed)
        combined_jobs = []
        for title, score in chroma_jobs:
            combined_jobs.append((title, 0.3 * score))
        for idx, row in filtered_bm25_jobs.iterrows():
            combined_jobs.append((row["job_title"], 0.7 * bm25_scores[idx]))

        # Sort the jobs based on the combined score and select the top 3
        sorted_jobs = sorted(combined_jobs, key=lambda x: x[1], reverse=True)[:3]

        # Format the results context by pulling details from the CSV
        if sorted_jobs:
            context = "\n".join([
                f"**{job[0]}**\n- Required Skills: {df[df['job_title'] == job[0]]['professional_skill_required'].values[0]}\n"
                f"- Salary: {df[df['job_title'] == job[0]]['offered_salary'].values[0]}\n"
                f"- Deadline: {df[df['job_title'] == job[0]]['deadline'].values[0]}\n"
                for job in sorted_jobs
            ])
        else:
            context = "No relevant jobs were found."

        # Construct the refined prompt for the career assistant
        prompt = (
            "You are a helpful career assistant. Your task is to provide job recommendations.\n"
            f"{context}\n\n"
            f"User Query: {user_query}\n\n"
            "Instructions:\n"
            "1. Only list jobs that are specifically relevant to the user's query.\n"
            "2. For each job, include job title, required skills, salary, and deadline.\n"
            "3. Format the response with bullet points for clarity.\n"
            "4. If no roles are found, politely inform the user.\n\n"
            "Now, respond to the user's query:"
        )
    else:
        # For non-job-related queries, simply pass the user query
        prompt = user_query

    # Generate Response using Ollama
    response = ollama.chat(
        model='llama2',
        messages=[{'role': 'user', 'content': prompt}]
    )

    return jsonify(response['message']['content'])

if __name__ == '__main__':
    app.run(debug=True)
