import spacy
import re
from spacy.matcher import Matcher
import nltk
from nltk.corpus import stopwords
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import io
import docx2txt
from typing import Optional

class CustomResumeParser:
    def __init__(self, resume_path: str):
        self.resume_path = resume_path
        self.nlp = spacy.load('en_core_web_sm')
        self.matcher = Matcher(self.nlp.vocab)
        self.text = ''
        
        # Get number of pages and extract text
        if resume_path.lower().endswith('.pdf'):
            self.text = extract_text(resume_path)
            self.no_of_pages = len(self.text.split('\f')) - 1  # Count form feeds
            if self.no_of_pages == 0:
                self.no_of_pages = 1
        elif resume_path.lower().endswith('.docx'):
            self.text = docx2txt.process(resume_path)
            self.no_of_pages = 1  # Approximate for Word docs
        else:
            raise ValueError("Unsupported file format. Please use PDF or DOCX files.")
                
        # Process the text with spaCy
        self.doc = self.nlp(self.text)
    
    def get_extracted_data(self) -> dict:
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
        
    def extract_name(self) -> str:
        # Simple name extraction using named entity recognition
        for ent in self.doc.ents:
            if ent.label_ == 'PERSON':
                return ent.text
        return ''
        
    def extract_email(self) -> str:
        # Extract email using regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, self.text)
        return emails[0] if emails else ''
        
    def extract_mobile_number(self) -> str:
        # Extract phone number using regex
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        numbers = re.findall(phone_pattern, self.text)
        return numbers[0] if numbers else ''
        
    def extract_skills(self) -> list:
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
        
    def extract_education(self) -> list:
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
        
    def extract_experience(self) -> list:
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
