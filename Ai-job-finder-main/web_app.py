import os
from flask import Flask, request, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
from app.parsers.pdf_parser import parse_resume_pdf
from app.nlp.extractor import extract_info
from app.search.job_fetcher import fetch_jobs
from app.matching.matcher import rank_jobs

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Job Finder</title>
    <style>
        body { font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f4f4f9; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .upload-box { border: 2px dashed #ccc; padding: 20px; text-align: center; margin-bottom: 20px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #0056b3; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        .match-score { font-weight: bold; color: #28a745; }
        .tag { background: #e9ecef; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; margin-right: 5px; }
        .source-badge { font-size: 0.8em; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI Resume Job Finder</h1>
        
        {% if not results %}
        <div class="upload-box">
            <p>Upload your Resume (PDF) to find matched jobs globally.</p>
            <p style="color: #666; font-size: 0.9em;">(Note: This searches for Remote jobs using your top skill)</p>
            <form action="/" method="post" enctype="multipart/form-data">
                <input type="file" name="resume" accept=".pdf" required>
                <br><br>
                <button type="submit" class="btn">Analyze & Find Jobs</button>
            </form>
        </div>
        {% else %}
        
        <div class="summary">
            <h3>Extracted Profile</h3>
            <p><strong>Detected Search Query:</strong> {{ query }}</p>
            <p><strong>Top Skills:</strong> 
                {% for skill in skills[:8] %}
                <span class="tag">{{ skill }}</span>
                {% endfor %}
            </p>
        </div>

        <h3>Top Matched Jobs</h3>
        <table>
            <thead>
                <tr>
                    <th>Match</th>
                    <th>Role</th>
                    <th>Company</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for job in results %}
                <tr>
                    <td><span class="match-score">{{ job.score }}%</span></td>
                    <td>
                        {{ job.title }}<br>
                        <span class="source-badge">via {{ job.source }}</span>
                    </td>
                    <td>{{ job.company }}<br><small>{{ job.location }}</small></td>
                    <td><a href="{{ job.url }}" target="_blank" class="btn" style="padding: 5px 10px; font-size: 0.8em;">Apply</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <br>
        <a href="/">Upload another resume</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            return redirect(request.url)
        
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # 1. Parse & Extract
                resume_text = parse_resume_pdf(filepath)
                extracted_data = extract_info(resume_text)
                
                skills = extracted_data['skills']
                designation = extracted_data['designation']
                
                # --- SMART SEARCH QUERY ---
                # Use only the FIRST skill (e.g., "Python") to ensure broad results.
                if skills:
                    search_query = skills[0]
                elif designation:
                    search_query = designation[0]
                else:
                    search_query = "dev"
                
                print(f"DEBUG: Searching for '{search_query}'...") 

                # 2. Fetch Jobs (Using Jobicy + Safety Net)
                jobs = fetch_jobs(search_query, limit=20)
                
                # 3. Rank Jobs
                ranked_jobs = rank_jobs(resume_text, jobs, top_k=10)
                
                return render_template_string(HTML_TEMPLATE, results=ranked_jobs, skills=skills, query=search_query)
            except Exception as e:
                return f"Error processing file: {str(e)}"
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)

    return render_template_string(HTML_TEMPLATE, results=None)

if __name__ == '__main__':
    app.run(debug=True)