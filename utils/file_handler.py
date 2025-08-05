import os
from werkzeug.utils import secure_filename

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not installed. PDF processing will be disabled.")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not installed. DOCX processing will be disabled.")

class FileHandler:
    def __init__(self, upload_folder='static/uploads'):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'pdf', 'docx', 'txt'}
        if not PDF_AVAILABLE:
            self.allowed_extensions.discard('pdf')
            print("PDF support disabled - install PyPDF2 to enable")
        if not DOCX_AVAILABLE:
            self.allowed_extensions.discard('docx')
            print("DOCX support disabled - install python-docx to enable")
        os.makedirs(upload_folder, exist_ok=True)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def save_file(self, file):
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)
            return file_path
        return None

    def extract_text_from_pdf(self, file_path):
        if not PDF_AVAILABLE:
            return "PDF processing not available. Please install PyPDF2."
        text = ''
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text_ = page.extract_text()
                    if text_:
                        text += text_
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return f"Error processing PDF: {str(e)}"
        return text

    def extract_text_from_docx(self, file_path):
        if not DOCX_AVAILABLE:
            return "DOCX processing not available. Please install python-docx."
        text = ''
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + '\n'
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return f"Error processing DOCX: {str(e)}"
        return text

    def extract_text_from_txt(self, file_path):
        text = ''
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
            except Exception as e:
                print(f"Error reading TXT file: {e}")
                return f"Error processing TXT: {str(e)}"
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return f"Error processing TXT: {str(e)}"
        return text

    def extract_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return self.extract_text_from_docx(file_path)
        elif ext == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            return f"Unsupported file type: {ext}"

    def get_supported_formats(self):
        return list(self.allowed_extensions)
