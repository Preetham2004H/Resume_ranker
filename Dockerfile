FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python - <<EOF
import nltk, os
nltk.download('punkt'); nltk.download('stopwords')
EOF
COPY . .
RUN mkdir -p static/uploads data/sample_resumes
ENV FLASK_APP=app.py FLASK_ENV=production
EXPOSE 5000
CMD ["gunicorn","--bind","0.0.0.0:5000","--workers","4","app:app"]
