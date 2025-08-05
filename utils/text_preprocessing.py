import re
import string

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import PorterStemmer

    # Download required NLTK data
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except:
        pass

    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available, using basic preprocessing")


class TextPreprocessor:
    def __init__(self):
        if NLTK_AVAILABLE:
            try:
                self.stop_words = set(stopwords.words('english'))
                self.stemmer = PorterStemmer()
            except:
                self.stop_words = set(
                    ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is',
                     'are', 'was', 'were'])
                self.stemmer = None
        else:
            self.stop_words = set(
                ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are',
                 'was', 'were'])
            self.stemmer = None

    def clean_text(self, text):
        """Clean and preprocess text data"""
        if not isinstance(text, str):
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove special characters but keep + and # (for C++, C#, etc.)
        text = re.sub(r'[^\w\s+#\.]', ' ', text)

        # Remove extra whitespaces
        text = ' '.join(text.split())

        return text

    def tokenize_and_remove_stopwords(self, text):
        """Tokenize text and remove stopwords"""
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(text)
            except:
                tokens = text.split()
        else:
            tokens = text.split()

        # Remove stopwords and very short tokens
        filtered_tokens = [
            token for token in tokens
            if token not in self.stop_words and len(token) > 1
        ]

        return filtered_tokens

    def stem_tokens(self, tokens):
        """Apply stemming to tokens"""
        if self.stemmer and NLTK_AVAILABLE:
            return [self.stemmer.stem(token) for token in tokens]
        return tokens

    def preprocess_text(self, text):
        """Complete text preprocessing pipeline"""
        # Clean text
        cleaned_text = self.clean_text(text)

        # If text is too short, return as-is
        if len(cleaned_text.strip()) < 10:
            return cleaned_text

        # Tokenize and remove stopwords
        tokens = self.tokenize_and_remove_stopwords(cleaned_text)

        # Apply stemming if available
        stemmed_tokens = self.stem_tokens(tokens)

        # Join tokens back to string
        processed_text = ' '.join(stemmed_tokens)

        # If processing resulted in empty text, return cleaned version
        return processed_text if processed_text.strip() else cleaned_text
