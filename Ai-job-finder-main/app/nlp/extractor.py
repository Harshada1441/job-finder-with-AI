import spacy
from spacy.matcher import PhraseMatcher
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("Model 'en_core_web_sm' not found. Downloading now...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

SKILL_KEYWORDS = [
    "Python", "Java", "C++", "C#", "SQL", "NoSQL", "TensorFlow", "PyTorch", 
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "React", "Angular", "Vue", 
    "Node.js", "Django", "Flask", "FastAPI", "Data Science", "Machine Learning", 
    "NLP", "Computer Vision", "Git", "Linux", "Rest API", "GraphQL", "Communication",
    "Excel", "Sales", "Marketing", "Design", "Writing"
]

def get_phrase_matcher(nlp_obj, terms):
    matcher = PhraseMatcher(nlp_obj.vocab, attr="LOWER")
    patterns = [nlp_obj.make_doc(text) for text in terms]
    matcher.add("SKILLS", patterns)
    return matcher

skill_matcher = get_phrase_matcher(nlp, SKILL_KEYWORDS)

def extract_years_experience(text: str) -> str:
    pattern = r"(\d+(\+)?\s*(years?|yrs?))"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0)
    return "Not specified"

def extract_info(text: str) -> dict:
    doc = nlp(text)
    
    skills_found = set()
    matches = skill_matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        skills_found.add(span.text)
    
    common_roles = ["Engineer", "Developer", "Scientist", "Analyst", "Manager", "Consultant"]
    designations = []
    for chunk in doc.noun_chunks:
        if any(role in chunk.text for role in common_roles):
            designations.append(chunk.text.strip())

    experience = extract_years_experience(text)

    # Sort skills by length (longer usually means more specific)
    # BUT we want to ensure we don't pick obscure ones first.
    # For now, let's just convert to list.
    skills_list = list(skills_found)
    
    # Priority sort: If "Python" or "Java" is there, put it first (better for Jobicy tags)
    priority_skills = ["Python", "Java", "React", "Node.js", "Go", "Ruby", "Data", "Design"]
    skills_list.sort(key=lambda x: x in priority_skills, reverse=True)

    return {
        "skills": skills_list,
        "designation": list(set(designations)),
        "experience": experience,
        "raw_text_len": len(text)
    }