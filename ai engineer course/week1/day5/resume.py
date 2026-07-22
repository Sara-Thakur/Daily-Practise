import os 
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
import time
from typing import List
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")
# my_project_id=os.getenv("GROQ_PROJECT_ID")

if not my_api_key :
    raise ValueError("API Key Kaha h bhai")

client=Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"

#to specify structure of answer 
job_desc="""
Software Engineer III, Infrastructure, Google Cloud
Minimum qualifications:
Bachelor’s degree or equivalent practical experience.
2 years of experience programming in C++, Java, Go or Python, or 1 year of experience with an advanced degree.

Preferred qualifications:
Master's degree or PhD in Computer Science or related technical fields.
2 years of experience building and developing large-scale infrastructure, distributed systems or networks, or experience with compute technologies, storage, or hardware architecture.
2 years of experience with data structures or algorithms in either an academic or industry setting.
Experience developing accessible technologies.
Responsibilities
Write product or system development code.
Participate in, or lead design reviews with peers and stakeholders to decide amongst available technologies.
Review code developed by other developers and provide feedback to ensure best practices (e.g., style guidelines, checking code in, accuracy, testability, and efficiency).
Contribute to existing documentation or educational content and adapt content based on product/program updates and user feedback.
Triage product or system issues and debug/track/resolve by analyzing the sources of issues and the impact on hardware, network, or service operations and quality.
"""

class MatchDetails(BaseModel):
    education_match: str | None = None
    experience_match: str | None = None
    skills_missing: List[str] | None = None

class MatchResult(BaseModel):
    score:float|None=None
    # details:dict  |None=None
    details:MatchDetails  |None=None
    name: str|None=None
    match: List[str] |None=None
    missing: List[str]|None=None
    overall_percentage: float|None=None
    final_verdict: str|None=None

class JobD(BaseModel):
   role:str|None=None
   required_skillSet:List[str]=[]
   preferred_skills:List[str]|None=None
   minimum_experience:List[str]|None=None
   educational_qualification:str|None=None
   responsibilties:str|None=None

job_schema=JobD.model_json_schema()

response_format={
    "type":"json_object"
}
system_prompt=f""""
You are an expert HR. 
Extract the actual information from the job description of the company 
to json format with  {job_schema} 
Do not invent the fields yourself. Do not return schema itself. If any detail in schema not present ,return null

"""
message_system={
    "role":"system",
    "content":system_prompt
}
user_prompt=f"""Analyse the foll owing job description{job_desc}"""
message_user={
        "role":"user",
        "content":user_prompt
    }

messages=[message_system,message_user]
response=client.chat.completions.create(model=model,messages=messages,response_format=response_format  )
answer=response.choices[0].message.content
# print(answer)
raw_json=answer
import json
# raw_json=answer

jobdata=json.loads(raw_json)
job=JobD(**jobdata)
#(**data_files)
print(job.minimum_experience)
print(job.educational_qualification)

### PArt 2 resume 

class Experience(BaseModel):
    role:str| None=None
    company:str| None=None
    duration:str| None=None
    skills_used:List[str]| None=None      
    description:str| None=None

class Resume(BaseModel):
    name:str| None=None
    email:str | None=None 
    phone_no:str | None=None
    skills:List[str]| None=None           
    projects:List[str]| None=None         
    experiences:List[Experience]| None=None
    total_experience_years:str | None=None
    education:List[str]| None=None
    certifications:List[str]| None=None
    
resume_schema=Resume.model_json_schema()

def parse_resume(resume_text):
    system_prompt=f""""
    You are an expert resume parser. 
    Extract the information based on its meaning 
    not only based on exact section headings
    from the resume of candidiate to valid json format matching with  {resume_schema}

    Different resumes may have different headings . 
    Example Professional experience ,work history,internships , experience.etc.
    skills may also appear in skills section , work experience , internships or projects.extract based on entire resume.

     Do not invent the fields yourself, 
    Do not return schema itself. 
    if a field is not present just write null/None
    Include internships inside experiences.
    """
    user_prompt=f"""Parse this resume {resume_text}"""
    message_system={
        "role":"system",
        "content":system_prompt
    }
    message_user={
        "role":"user",
        "content":user_prompt
    }
    messages=[message_system,message_user]
    response_format={
        "type":"json_object"
    }
    response=client.chat.completions.create(model=model,messages=messages,response_format=response_format  )
    raw_out=response.choices[0].message.content
    data=json.loads(raw_out)
    return Resume(**data)


# parsed_resume=parse_resume

from pypdf import PdfReader
def read_pdf(file_path):
    reader=PdfReader(file_path)
    text=""
    for page in reader.pages:
        page_text=page.extract_text()
        if page_text:
            text+=page_text+"\n"
    return text

from docx import Document
def read_docx(file_path):
    # Load the document
    doc = Document(file_path)
    text=""
    # Store text from each paragraph
    # text_content = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text+=paragraph.text+"\n"
        # text_content.append(paragraph.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text+=cell.text+"\n"
    return text


def read_resume(file_path):
    suffix = Path(file_path).suffix.lower()
    if suffix == '.pdf':
        return read_pdf(file_path)
    elif suffix == '.docx':
        return read_docx(file_path)
    else:
        return None
 
def final_score(job,resume):
     match_schema=MatchResult.model_json_schema()
     prompt=f""""You are an HR recruiter. 
     
     Match the job description{job.model_dump_json(indent=2)}
       ,and resume {resume.model_dump_json(indent=2)}
       .and give details( name, match, missing, overall percentage, short final verdict)
       in a short way.
       Provide the score as a percentage between 0 and 100.
         score for the candiadiates 
       in json format with schema{match_schema}. 
       keep the response concise and easy to read"""
     message={
         "role":"user",
         "content":prompt
     }
     
     messages=[message]
     response_format={
         "type":"json_object"
     }
     response=client.chat.completions.create(model=model,messages=messages,response_format=response_format  )
     data=json.loads(response.choices[0].message.content)
     return MatchResult(**data)
   
resume_folder=Path("resumes")
#C:\Users\PC\practise_with_me\week1\day5\resumes\Bhautik_Resume.pdf
all_results=[]
for file_path in resume_folder.iterdir():
    if file_path.suffix.lower() not in [".pdf",".docx"]:
        continue
    print("\n Preprocessing:",file_path.name)

    resume_text=read_resume(file_path)
    parsed_resume=parse_resume(resume_text)
    time.sleep(5)
    result=final_score(job,parsed_resume)
    time.sleep(5) #to prevent denial oof service in software
    # print("Name:",parsed_resume.name)
    print("Score:",result.score)
    all_results.append({
        "name":parsed_resume.name,
        "score":result.score,
        "details":result.details
    })
all_results.sort(key=lambda x: x["score"] if x["score"] is not None else 0, reverse=True)
top_2=all_results[:2]
worst_2=all_results[-2:]


response_format={
    "type":"json_object"
}

 


print("TOp two")
for candidate in top_2:
    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%",
        )
    print (candidate["details"]
)
print("worst two")
for candidate in worst_2:
    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%",
        )
    print (candidate["details"]
)
 