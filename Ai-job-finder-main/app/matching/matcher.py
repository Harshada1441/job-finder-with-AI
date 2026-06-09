from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.utils.logger import get_logger

logger = get_logger(__name__)

_MODEL = None

def get_model():
    global _MODEL
    if _MODEL is None:
        logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
        _MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    return _MODEL

def rank_jobs(resume_text: str, jobs: list, top_k: int = 5) -> list:
    if not jobs:
        return []

    model = get_model()
    resume_embedding = model.encode([resume_text])
    job_texts = [job['description'] for job in jobs]
    job_embeddings = model.encode(job_texts)
    
    scores = cosine_similarity(resume_embedding, job_embeddings)[0]
    
    ranked_jobs = []
    for i, job in enumerate(jobs):
        score_percent = round(scores[i] * 100, 2)
        job['score'] = score_percent
        ranked_jobs.append(job)
        
    ranked_jobs.sort(key=lambda x: x['score'], reverse=True)
    
    return ranked_jobs[:top_k]