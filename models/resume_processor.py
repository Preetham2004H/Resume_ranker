import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from utils.text_preprocessing import TextPreprocessor


class ResumeProcessor:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english'
        )

    def extract_skills(self, text):
        """Extract technical skills from resume text"""
        skills_keywords = [
            'python', 'java', 'javascript', 'sql', 'mongodb', 'react', 'angular',
            'machine learning', 'data science', 'artificial intelligence', 'ai',
            'flask', 'django', 'nodejs', 'express', 'html', 'css', 'bootstrap',
            'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'cloud',
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch',
            'mysql', 'postgresql', 'redis', 'spark', 'hadoop', 'big data',
            'tableau', 'power bi', 'excel', 'api', 'rest', 'json', 'xml',
            'linux', 'windows', 'devops', 'ci/cd', 'agile', 'scrum',
            'spring', 'hibernate', 'microservices', 'web development',
            'mobile development', 'android', 'ios', 'swift', 'kotlin'
        ]

        text_lower = text.lower()
        found_skills = []

        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append(skill)

        # Remove duplicates and return
        return list(set(found_skills))

    def process_resume(self, resume_text):
        """Process individual resume"""
        try:
            # Clean the text first
            cleaned_text = resume_text.strip()
            if not cleaned_text:
                return {
                    'original_text': resume_text,
                    'processed_text': '',
                    'skills': [],
                    'skill_count': 0
                }

            # Preprocess text for matching
            processed_text = self.preprocessor.preprocess_text(cleaned_text)

            # Extract skills from original text (better detection)
            skills = self.extract_skills(cleaned_text)

            print(f"DEBUG: Processed text length: {len(processed_text)}")
            print(f"DEBUG: Skills found: {skills}")

            return {
                'original_text': resume_text,
                'processed_text': processed_text if processed_text.strip() else cleaned_text.lower(),
                'skills': skills,
                'skill_count': len(skills)
            }
        except Exception as e:
            print(f"Error processing resume: {e}")
            # Return fallback processing
            return {
                'original_text': resume_text,
                'processed_text': resume_text.lower(),
                'skills': [],
                'skill_count': 0
            }
