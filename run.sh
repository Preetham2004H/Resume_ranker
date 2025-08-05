#!/bin/bash
echo "🚀 Starting Resume Ranker"
if ! command -v python3 &>/dev/null; then echo "Python3 required"; exit 1; fi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python - <<EOF
import nltk
nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)
EOF
mkdir -p static/uploads data/sample_resumes
python app.py
