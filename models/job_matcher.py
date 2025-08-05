# D:\k\models\job_matcher.py
# -------------------------------------------------
#  Author : Resume-Ranker demo
#  Purpose: Rank multiple resumes against a single
#           job-description using TF-IDF + cosine
# -------------------------------------------------

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class JobMatcher:
    """Compute similarity between a job-description and many resumes."""

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            max_features=1_000,         # limited vocabulary keeps RAM low
            ngram_range=(1, 3),
            stop_words="english",
            min_df=1,
            max_df=0.80,
            lowercase=True,
            token_pattern=r"[a-zA-Z][a-zA-Z+#\.]{2,}",
        )

    # ------------------------------------------------------------------ #
    #  PUBLIC API                                                         #
    # ------------------------------------------------------------------ #
    def rank_resumes(self, resumes_data: list, job_description: str) -> list:
        """
        Return a list of dicts—one per resume—sorted by highest similarity.

        Each dict contains:
            resume_id          index in the original list
            filename           original filename if provided
            similarity_score   raw cosine value (0-1)
            percentage_match   similarity_score * 100, rounded to 2-dec
            skills             list of skills extracted (if provided)
            skill_count        len(skills)
            rank               1 = best match
        """
        # Guard clauses
        if not resumes_data or not job_description.strip():
            print("DEBUG: rank_resumes – empty input")
            return []

        # --------------------------------------------------------------- #
        # 1. Build the corpus: JD first, then every resume’s processed
        #    text (fall-back to original text if missing).
        # --------------------------------------------------------------- #
        documents = [job_description.lower().strip()]
        for res in resumes_data:
            text = (
                res.get("processed_text", "") if isinstance(res, dict) else str(res)
            ).strip()
            if not text:
                text = (res.get("original_text", "") if isinstance(res, dict) else "").lower()
            documents.append(text.lower())

        # --------------------------------------------------------------- #
        # 2. TF-IDF vectorisation and cosine similarity
        # --------------------------------------------------------------- #
        tfidf = self.vectorizer.fit_transform(documents)
        job_vec = tfidf[0:1]          # first row = Job Description
        resume_vecs = tfidf[1:]       # remaining rows = resumes

        sims = cosine_similarity(job_vec, resume_vecs).flatten()
        # sims is a numpy array of floats in [0,1]

        # --------------------------------------------------------------- #
        # 3. Assemble result objects
        # --------------------------------------------------------------- #
        results = []
        for idx, score in enumerate(sims):
            pct = round(float(score) * 100, 2)  # to percentage, two decimals
            res_meta = resumes_data[idx] if isinstance(resumes_data[idx], dict) else {}

            results.append(
                {
                    "resume_id": idx,
                    "filename": res_meta.get("filename", f"Resume_{idx+1}"),
                    "similarity_score": float(score),
                    "percentage_match": pct,
                    "skills": res_meta.get("skills", []),
                    "skill_count": res_meta.get("skill_count", 0),
                }
            )

        # --------------------------------------------------------------- #
        # 4. Sort & rank (most similar first)
        # --------------------------------------------------------------- #
        results.sort(key=lambda r: r["similarity_score"], reverse=True)
        for rank, obj in enumerate(results, 1):
            obj["rank"] = rank

        # Optional DEBUG snippet (no nested f-strings!)
        top3 = [f"{r['filename']} – {r['percentage_match']}%" for r in results[:3]]
        print("DEBUG: Final ranking (top-3):", top3)

        return results

    # ------------------------------------------------------------------ #
    #  Helper: raw similarity vector (not used by the app, but handy)
    # ------------------------------------------------------------------ #
    def calculate_similarity_scores(
        self, resumes_data: list, job_description: str
    ) -> np.ndarray:
        """Return a NumPy array of cosine similarities in the original order."""
        if not resumes_data or not job_description.strip():
            return np.zeros(len(resumes_data))

        docs = [job_description.lower().strip()]
        for res in resumes_data:
            text = (
                res.get("processed_text", "") if isinstance(res, dict) else str(res)
            ).strip()
            if not text:
                text = (res.get("original_text", "") if isinstance(res, dict) else "").lower()
            docs.append(text.lower())

        tfidf = self.vectorizer.fit_transform(docs)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        return sims
