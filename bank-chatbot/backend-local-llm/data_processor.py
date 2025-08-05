import fitz
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import PDF_PATH

# --- PDF Processing and Embedding ---
text_chunks = []
model = None
index = None

def initialize_data():
    """Initializes and loads the PDF data and FAISS index."""
    global text_chunks, model, index
    try:
        with fitz.open(PDF_PATH) as doc:
            for page in doc:
                page_text = page.get_text()
                lines = page_text.split('\n')
                for line in lines:
                    stripped_line = line.strip()
                    if len(stripped_line) > 20:
                        text_chunks.append(stripped_line)
        
        if not text_chunks:
            print("Warning: No significant text chunks extracted from the PDF. Check the PDF content or the chunking logic.")
            text_chunks = ["Could not load the PDF document or process the information. Please contact support."]
        
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(text_chunks)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings))
        print(f"Loaded {len(text_chunks)} text chunks from the PDF and created the FAISS index.")
    except Exception as e:
        print(f"Error processing PDF or generating embeddings: {e}")
        text_chunks = ["Could not load the PDF document or process the information. Please contact support."]
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(text_chunks)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings))

def search_similar_chunks(question, k=4):
    """Searches for similar text chunks in the PDF embeddings."""
    if not text_chunks:
        return "No information available from the document."
    q_embed = model.encode([question])
    D, I = index.search(np.array(q_embed), k=k)
    return "\n".join([text_chunks[i] for i in I[0]])

# Initialize data on import
initialize_data()