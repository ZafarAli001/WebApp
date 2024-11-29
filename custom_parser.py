import spacy
import re
from spacy.matcher import Matcher
import nltk
from nltk.corpus import stopwords
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io

class CustomResumeParser:
    def __init__(self, resume_path):
        self.resume_path = resume_path
        self.nlp = spacy.load('en_core_web_sm')
        self.matcher = Matcher(self.nlp.vocab)
        self.text = ''
        
        # Get number of pages
        self.no_of_pages = 0
        with open(resume_path, 'rb') as file:
            for page in PDFPage.get_pages(file):
                self.no_of_pages += 1
        
        # Extract text from PDF
        self.text = self.extract_text_from_pdf()
                
        # Process the text with spaCy
        self.doc = self.nlp(self.text)
    
    def extract_text_from_pdf(self):
        # Extract text from pdf file
        with open(self.resume_path, 'rb') as fh:
            # PDFMiner boilerplate
            rsrcmgr = PDFResourceManager()
            sio = io.StringIO()
            codec = 'utf-8'
            laparams = LAParams()
            device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                interpreter.process_page(page)

            text = sio.getvalue()

            device.close()
            sio.close()

            return text
        
    def get_extracted_data(self):
        data = {
            'name': self.extract_name(),
            'email': self.extract_email(),
            'mobile_number': self.extract_mobile_number(),
            'skills': self.extract_skills(),
            'education': self.extract_education(),
            'experience': self.extract_experience(),
            'no_of_pages': self.no_of_pages
        }
        return data
        
    def extract_name(self):
        # Simple name extraction using named entity recognition
        for ent in self.doc.ents:
            if ent.label_ == 'PERSON':
                return ent.text
        return ''
        
    def extract_email(self):
        # Extract email using regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, self.text)
        return emails[0] if emails else ''
        
    def extract_mobile_number(self):
        # Extract phone number using regex
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        numbers = re.findall(phone_pattern, self.text)
        return numbers[0] if numbers else ''
        
    def extract_skills(self):
        # Common programming languages and technologies
        skills_pattern = [
            'python', 'java', 'c++', 'javascript', 'html', 'css', 'sql',
            'react', 'angular', 'vue', 'node', 'django', 'flask',
            'aws', 'docker', 'kubernetes', 'git', 'machine learning',
            'data science', 'artificial intelligence', 'ai', 'ml',
            'database', 'mongodb', 'postgresql', 'mysql'
        ]
        
        found_skills = []
        for token in self.doc:
            if token.text.lower() in skills_pattern:
                found_skills.append(token.text)
                
        return list(set(found_skills))
        
    def extract_education(self):
        # Education-related keywords
        education_pattern = [
            'bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'degree',
            'university', 'college', 'school', 'institute'
        ]
        
        education = []
        for sent in self.doc.sents:
            for pattern in education_pattern:
                if pattern in sent.text.lower():
                    education.append(sent.text.strip())
                    break
                    
        return list(set(education))
        
    def extract_experience(self):
        # Experience-related keywords
        exp_pattern = [
            'experience', 'work', 'job', 'company', 'position',
            'role', 'responsibility'
        ]
        
        experience = []
        for sent in self.doc.sents:
            for pattern in exp_pattern:
                if pattern in sent.text.lower():
                    experience.append(sent.text.strip())
                    break
                    
        return list(set(experience))
