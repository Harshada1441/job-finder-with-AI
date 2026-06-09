import pytest
from app.matching.matcher import rank_jobs

def test_ranking_logic():
    resume = "I am a Python developer with Flask experience."
    
    jobs = [
        {"title": "Chef", "description": "Cooking food in a kitchen", "url": "", "location": "", "company": ""},
        {"title": "Python Dev", "description": "Writing Python code and Flask apps", "url": "", "location": "", "company": ""}
    ]
    
    ranked = rank_jobs(resume, jobs, top_k=2)
    
    assert ranked[0]['title'] == "Python Dev"
    assert ranked[0]['score'] > ranked[1]['score']