import pandas as pd
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS



def processing(df:pd):
    '''
    A function to process, lowercase , removing stopowords and tokenization
    '''

# filling missing values
    df.fillna({"company_name": "Unknown", 
            "job_category" : "Unknown",
            "job_level" : "Unknown",
            "employment_type" : "Unknown",
            "job_location" : "Unknown",
            "offered_salary" : "Not Disclosed",
            "professional_skill_required" : "Versatile",
            "education_level" : "Bachelors Passed",
            "experience_required" : "Not Disclosed",
            "no_of_vacancy" : 0
            },inplace=True)


    # no-of-vacancy:str to int
    df['no_of_vacancy'] = df['no_of_vacancy'].astype(int)


    #taking colums to process on..
    text_columns = ["job_title", "job_category", "job_level", "employment_type", 
                    "job_location", "education_level", "experience_required", "professional_skill_required"]

    # text process
    for col in text_columns:
        df[col] = df[col].apply(preprocess_text)

    # process employment
    df["employment_type"] = df["employment_type"].apply(fix_employment_type)

    # normalizing experience
    df["experience_required"] = df["experience_required"].apply(normalize_experience)

    # extracting skiils
    df["professional_skill_required"] = df["professional_skill_required"].apply(extract_skills)

    # save the processed stuff to new csv
    df.to_csv("/home/san/Desktop/jobot/data/processed/processed_jobfile.csv",index = False)


# regex and removing stopwords a,an,the
def preprocess_text(text):
    text = text.lower()  #lowercase
    text = re.sub(r'[^\w\s]', '', text)  #punctuation, specialchars
    tokens = text.split()  #tokens with spaces
    tokens = [word for word in tokens if word not in ENGLISH_STOP_WORDS]  #english stop words for removing stopwords
    
    return " ".join(tokens)


# pricessing the text,and cleaning for it to give more context
def fix_employment_type(text):
    if "full" in text:
        return "full-time"
    elif "part" in text:
        return "part-time"
    return "unknown"

# context giving texts on experience
def normalize_experience(text):
    match = re.search(r'(\d+)', text)  #extract years
    if match:
        return f"{match.group(1)} years experience"
    return "not specified"

# extracting skills
def extract_skills(text):
    skills = text.split()  
    skills = list(set(skills))  # removing duplicates
    return ", ".join(skills)

if __name__ == "__main__":
    df = pd.read_csv("/home/san/Desktop/jobot/data/raw/jobfile.csv")
    processing(df)