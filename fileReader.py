import textract as tx
import pandas as pd
import os
import requests
import json
import re


url = "https://jn6onwb95l.execute-api.ap-south-1.amazonaws.com/api2_check"
headers = {'Content-Type': 'text/plain'}


def makeRequest(payload):
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


def getEntities(text):
    res = makeRequest(text.encode(encoding='UTF-8', errors='strict'))
    rej = json.loads(res)
    df1 = pd.json_normalize(rej, record_path=['Entities'])
    df2 = df1.drop_duplicates(subset=['Text']).dropna()
    # return df2[(df2.Type=='TITLE')]['Text'].tolist() + df2[df2.Type=='ORGANIZATION']['Text'].tolist()
    # return [x.upper() for x in df2[(df2.Type=='TITLE')]['Text'].tolist()]
    rs = df2[(df2.Type == 'TITLE')]['Text'].tolist()
    if(rs==None or len(rs)==0 ):
        rs.append("NAN")
    return [re.sub('[^a-zA-Z0-9 ]+', '', s).strip().upper() for s in rs]


def read_resumes(list_of_resumes, resume_directory):
    placeholder = []
    for res in list_of_resumes:
        print("prcessing Resume:" + res)
        temp = [res]
        text = tx.process(os.path.join(resume_directory , res), encoding='ascii')
        text = str(text, 'utf-8')
        temp.append(text)
        placeholder.append(temp)
    return placeholder


def get_cleaned_words(document):
    for i in range(len(document)):
        document[i].append(",".join(getEntities(document[i][1])))
    return document


# Database.to_json("Resume_Data.json", index=False)

def read_jobdescriptions(job_description_names, job_desc_dir):
    placeholder = []
    for tes in job_description_names:
        print("prcessing JD:" + tes)
        temp = []
        temp.append(tes)
        text = tx.process(os.path.join(job_desc_dir, tes), encoding='ascii')
        text = str(text, 'utf-8')
        temp.append(text)
        placeholder.append(temp)
    return placeholder


def execution(parent_path,resume_names,job_description_names):

    resume_dir=os.path.join(parent_path, 'Resumes')
    job_desc_dir=os.path.join(parent_path, 'JobDesc')
    # resume_names = os.listdir(resume_dir)
    # job_description_names = os.listdir(job_desc_dir)

    document = read_resumes(resume_names, resume_dir)
    Doc = get_cleaned_words(document)
    Database = pd.DataFrame(Doc, columns=["Name", "Context", "Entities"])
    Database.to_csv(os.path.join(parent_path,"Resume_Data.csv"), index=False)

    job_document = read_jobdescriptions(job_description_names, job_desc_dir)
    Jd = get_cleaned_words(job_document)
    jd_database = pd.DataFrame(Jd, columns=["Name", "Context", "Entities"])
    jd_database.to_csv(os.path.join(parent_path,"Job_Data.csv"), index=False)


#parent_path = os.path.join(os.getcwd(), 'data', "jsmith")
#execution(parent_path)