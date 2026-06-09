import pytest
from app.nlp.extractor import extract_info

@pytest.fixture
def sample_text():
    return """
    Jane Doe
    Senior Software Engineer
    5+ years of experience in Python, AWS, and Docker.
    Looking for a remote role.
    """

def test_nlp_extraction(sample_text):
    data = extract_info(sample_text)
    
    assert "Python" in data['skills']
    assert "AWS" in data['skills']
    assert "Docker" in data['skills']
    assert "5+ years" in data['experience']