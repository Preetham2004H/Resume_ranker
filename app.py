from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os

# Import custom modules
from utils.file_handler import FileHandler
from models.resume_processor import ResumeProcessor
from models.job_matcher import JobMatcher

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize components
file_handler = FileHandler(app.config['UPLOAD_FOLDER'])
resume_processor = ResumeProcessor()
job_matcher = JobMatcher()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_resumes():
    if request.method == 'POST':
        # Get multiple files and job description
        files = request.files.getlist('resumes')  # This gets ALL selected files
        job_description = request.form.get('job_description', '').strip()

        print(f"DEBUG: Received {len(files)} files")
        print(f"DEBUG: Job description length: {len(job_description)}")

        # Validation
        if not job_description:
            flash('Job description is required', 'error')
            return render_template('upload.html')

        if not files or all(f.filename == '' for f in files):
            flash('Please upload at least one resume file', 'error')
            return render_template('upload.html')

        # Process ALL uploaded files
        resume_data = []
        processed_count = 0

        for file in files:
            if file.filename == '':
                continue

            print(f"DEBUG: Processing file: {file.filename}")

            # Check file type
            if not file_handler.allowed_file(file.filename):
                flash(f'File type not supported: {file.filename}', 'warning')
                continue

            # Save file
            file_path = file_handler.save_file(file)
            if not file_path:
                flash(f'Could not save file: {file.filename}', 'warning')
                continue

            # Extract text from file
            resume_text = file_handler.extract_text(file_path)

            if not resume_text or len(resume_text.strip()) < 50:  # Minimum text length
                flash(f'Could not extract sufficient text from: {file.filename}', 'warning')
                continue

            print(f"DEBUG: Extracted {len(resume_text)} characters from {file.filename}")

            # Process resume text
            try:
                processed = resume_processor.process_resume(resume_text)
                processed['filename'] = file.filename
                resume_data.append(processed)
                processed_count += 1
                print(f"DEBUG: Successfully processed {file.filename}")
            except Exception as e:
                print(f"ERROR: Failed to process {file.filename}: {e}")
                flash(f'Error processing {file.filename}: {str(e)}', 'warning')
                continue

        # Check if we have any valid resumes
        if not resume_data:
            flash('No valid resumes were processed. Please check your files.', 'error')
            return render_template('upload.html')

        print(f"DEBUG: Successfully processed {processed_count} out of {len(files)} files")

        # Rank ALL resumes by percentage match
        try:
            results = job_matcher.rank_resumes(resume_data, job_description)

            if not results:
                flash('Could not rank resumes. Please try again.', 'error')
                return render_template('upload.html')

            print(f"DEBUG: Ranked {len(results)} resumes")
            for i, result in enumerate(results[:3]):  # Show top 3
                print(f"DEBUG: Rank {i + 1}: {result['filename']} - {result['percentage_match']}%")

            # Add success message
            flash(f'Successfully ranked {len(results)} resumes!', 'success')

            return render_template('results.html',
                                   results=results,
                                   job_description=job_description,
                                   total_resumes=len(results))

        except Exception as e:
            print(f"ERROR: Ranking failed: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error ranking resumes: {str(e)}', 'error')
            return render_template('upload.html')

    return render_template('upload.html')


@app.route('/demo')
def demo():
    # Sample data for demonstration
    job_description = """We are looking for a Python Developer with experience in machine learning, 
    data science, and web development. Requirements: Python, Flask, scikit-learn, pandas, SQL, 
    REST APIs, Git, and cloud platforms like AWS."""

    sample_resumes = [
        {
            'filename': 'john_doe_senior.pdf',
            'text': '''John Doe - Senior Python Developer
            5 years experience in Python development, machine learning, and data science.
            Skills: Python, Flask, Django, scikit-learn, pandas, numpy, SQL, PostgreSQL, 
            REST APIs, Git, AWS, Docker, machine learning algorithms, data analysis.
            Experience with TensorFlow, Keras, and deep learning projects.'''
        },
        {
            'filename': 'jane_smith_fullstack.pdf',
            'text': '''Jane Smith - Full Stack Developer
            3 years experience in web development. Some Python experience.
            Skills: JavaScript, React, Node.js, Python, HTML, CSS, MongoDB, 
            Express.js, Git, basic machine learning knowledge.'''
        },
        {
            'filename': 'mike_jones_data.pdf',
            'text': '''Mike Jones - Data Scientist
            4 years in data science and analytics. Strong Python background.
            Skills: Python, pandas, numpy, scikit-learn, matplotlib, seaborn,
            SQL, Jupyter, statistics, machine learning, data visualization,
            AWS, big data processing.'''
        }
    ]

    # Process sample resumes
    resume_data = []
    for resume in sample_resumes:
        processed = resume_processor.process_resume(resume['text'])
        processed['filename'] = resume['filename']
        resume_data.append(processed)

    # Rank resumes by percentage
    results = job_matcher.rank_resumes(resume_data, job_description)

    return render_template('results.html',
                           results=results,
                           job_description=job_description,
                           total_resumes=len(resume_data),
                           is_demo=True)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
