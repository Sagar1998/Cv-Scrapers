import matplotlib.colors as mcolors
import gensim
import gensim.corpora as corpora
from operator import index
from wordcloud import WordCloud
from pandas._config.config import options
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import Similar
from PIL import Image
import time
import os
import page 
import pdftotext
import spacy
from spacy.pipeline import EntityRuler
from spacy import displacy
import jsonlines
# nlp = spacy.load('en_core_web_sm')
import pandas as pd
import base64
from matplotlib_venn_wordcloud import venn2_wordcloud
import requests
import json 
import re
if not st.session_state["authentication_status"]or (not st.session_state["st_user"] ):
    st.write('Please login')    
    st.stop()
us=""

if 'st_user' in st.session_state:
    us=st.session_state['st_user']
parent_path = os.path.join(os.getcwd(), 'data', us)

image = Image.open('Images//logo.png')
st.image(image, use_column_width=True)

st.title("Resume Matcher")


# Reading the CSV files prepared by the fileReader.py
Resumes = pd.read_csv(os.path.join(parent_path,'Resume_Data.csv'))
Jobs = pd.read_csv(os.path.join(parent_path,'Job_Data.csv'))


############################### JOB DESCRIPTION CODE ######################################
# Checking for Multiple Job Descriptions
# If more than one Job Descriptions are available, it asks user to select one as well.
if len(Jobs['Name']) <= 1:
    st.write(
        "There is only 1 Job Description present. It will be used to create scores.")
else:
    st.write("There are ", len(Jobs['Name']),
             "Job Descriptions available. Please select one.")
st.markdown("---")
col_jd1,col_jd2=st.columns((1,1))
with col_jd1:
    option_tn = st.selectbox("Select Job Description ?", options=list(Jobs['Name']))
    option_yn = st.selectbox("Show the Job Description ?", options=['YES', 'NO'])
index=list(Jobs.index[Jobs['Name'] == option_tn])[0]
with col_jd2:
    if option_yn == 'YES':
        st.markdown("#### Job Description :")
        fig = go.Figure(data=[go.Table(
            header=dict(values=["Job Description"],
                        fill_color='#f0a500',
                        align='center', font=dict(color='white', size=16)),
            cells=dict(values=[Jobs['Context'][index]],
                    fill_color='#f4f4f4',
                    align='left'))])

        fig.update_layout(width=800, height=400)
        st.write(fig)
st.markdown("---")


#################################### SCORE CALCUATION ################################

    
def match_skills(jd_skillset, cv_skillset,resume_name):
    '''Get intersection of resume skills and job offer skills and return match percentage'''

    if len(jd_skillset) < 1:
        print('could not extract skills from job offer text')   
    else:
        pct_match = round(len(jd_skillset.intersection(cv_skillset)) / len(jd_skillset) * 100, 0)
        return (resume_name, pct_match,list(jd_skillset ))


# with jsonlines.open( "Data/skill_patterns.jsonl") as f:
#     created_entities = [line['label'].upper() for line in f.iter()]
skillset_dict={}
for i in range(len(Resumes['Name'])):
    skillset_dict[Resumes['Name'][i]]=(Resumes['Entities'][i]).split(",")
print("skillset_dict")
print(skillset_dict)
jd_skillset = (Jobs['Entities'][index]).split(",")
print("jd_skillset")
print(jd_skillset)

# Create a list with tuple pairs containing the names of the candidates and their match percentage
finn=[]
scores_final=[]
match_pairs = [match_skills(set(jd_skillset), set(skillset_dict[name]), name) for name in skillset_dict.keys()]
for i in match_pairs:
    scores_final.append(i)
for i in range(len(scores_final)):
    finn.append(scores_final[i][1])


############ TODO SCORE IMPROVEMENT"####################


Resumes['Scores'] = finn

Ranked_resumes = Resumes.sort_values(
    by=['Scores'], ascending=False).reset_index(drop=True)

Ranked_resumes['Rank'] = pd.DataFrame(
    [i for i in range(1, len(Ranked_resumes['Scores'])+1)])



###################################### SCORE TABLE PLOT ####################################

fig1 = go.Figure(data=[go.Table(
    header=dict(values=["Rank", "Name", "Scores"],
                fill_color='#00416d',
                align='center', font=dict(color='white', size=16)),
    cells=dict(values=[Ranked_resumes.Rank, Ranked_resumes.Name, Ranked_resumes.Scores],
               fill_color='#d6e0f0',
               align='left'))])
#st.write(fig1.to_html(),unsafe_allow_html=True)




fig1.update_layout(title="Top Ranked Resumes", width=700, height=800)
st.write(fig1,unsafe_allow_html=True)

org_Ranked_resumes=list(Ranked_resumes['Name'])

@st.cache
def convert_df_to_csv(df):
  # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df.to_csv(index=False).encode('utf-8')

exp_df=Ranked_resumes[['Rank',"Name",'Scores']]
st.download_button(
  label="Download results as CSV",
  data=convert_df_to_csv(exp_df),
  file_name='Top_resumes.csv',
  mime='text/csv'
)

resume_dir = os.path.join(parent_path,"Resumes")
def encode(fx):
    es=None
    with open(fx, "rb") as image_file:
        es= base64.b64encode(image_file.read())
    return es
for i in range(len(Ranked_resumes['Name'])):
    es=encode(os.path.join(resume_dir,Ranked_resumes['Name'][i]))
    Ranked_resumes['Name'][i]=f'<a href="data:file/csv;base64,'+es.decode()+'" download="'+Ranked_resumes['Name'][i]+'">'+Ranked_resumes['Name'][i]+'</a>'

#st.markdown(Ranked_resumes[['Rank',"Name",'Scores']].to_html(render_links=True, escape=False, index=False),unsafe_allow_html=True)
#Ranked_resumes[['Rank',"Name",'Scores']].to_json('test.json')
with st.expander("Download Top Resumes"):
    st.write(Ranked_resumes[['Rank',"Name",'Scores']].to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")
############################################ TF-IDF Code ###################################

col1,col2=st.columns((1,1))

fig2 = px.bar(Ranked_resumes,
              x=Ranked_resumes['Name'], y=Ranked_resumes['Scores'], color='Scores',
              color_continuous_scale='haline', title="Score and Rank Distribution")
# fig.update_layout(width=700, height=700)
with col1:
    st.plotly_chart(fig2, use_container_width=True)
    #st.write(fig2)


st.markdown("---")

############################################ TF-IDF Code ###################################


@st.cache()
def get_list_of_words(document):
    Document = []

    for a in document:
        raw = a.split(",")
        Document.append(raw)

    return Document


document = get_list_of_words(Resumes['Entities'])

id2word = corpora.Dictionary(document)
corpus = [id2word.doc2bow(text) for text in document]


lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=id2word, num_topics=6, random_state=100,
                                            update_every=3, chunksize=100, passes=50, alpha='auto', per_word_topics=True)

################################### LDA CODE ##############################################


@st.cache  # Trying to improve performance by reducing the rerun computations
def format_topics_sentences(ldamodel, corpus):
    sent_topics_df = []
    for i, row_list in enumerate(ldamodel[corpus]):
        row = row_list[0] if ldamodel.per_word_topics else row_list
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df.append(
                    [i, int(topic_num), round(prop_topic, 4)*100, topic_keywords])
            else:
                break

    return sent_topics_df


################################# Topic Word Cloud Code #####################################
# st.sidebar.button('Hit Me')
with col2:
    sel_resume = st.selectbox("Select resume ", options=org_Ranked_resumes)
# st.text(temp[0][sel_resume])


    wordcloud = WordCloud(background_color='white').generate(" ".join(skillset_dict[sel_resume]))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    st.pyplot(plt)
    #print(jd_skillset)

#st.markdown("---")

####################### SETTING UP THE DATAFRAME FOR SUNBURST-GRAPH ############################



fig, ax = plt.subplots(figsize=(10,10))
ax.set_title("Venn digram for Job features Vs resume", fontsize=20)
v = venn2_wordcloud([set(jd_skillset), set(skillset_dict[sel_resume])],
                    ax=ax, set_labels=["Job Features", "Resume :"+sel_resume])
# add color
v.get_patch_by_id("10").set_color("red")
v.get_patch_by_id("10").set_alpha(0.4)
v.get_patch_by_id("01").set_color("blue")
v.get_patch_by_id("01").set_alpha(0.4)
v.get_patch_by_id("11").set_color("purple")
v.get_patch_by_id("11").set_alpha(0.4)
st.pyplot(fig)




############################## RESUME PRINTING #############################

with st.form(key="Form1 :", clear_on_submit = False):
    s_file = st.select_slider(
        'Select the resume to display',
        options=org_Ranked_resumes)
    Submit3 = st.form_submit_button(label='Submit')

import mammoth
if Submit3:
    file_path=os.path.join(resume_dir,s_file)
    if(s_file.split('.')[-1]=='pdf'):
        with open(file_path,"rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
    elif(s_file.split('.')[-1]=='docx'):
        text=mammoth.convert_to_markdown(file_path).value
        #st.markdown("#### {0} :".format(s_file))
        fig = go.Figure(data=[go.Table(
            header=dict(values=[s_file],
                        fill_color='#f0a500',
                        align='center', font=dict(color='white', size=16)),
            cells=dict(values=[text],
                    fill_color='#f4f4f4',
                    align='left'))])

        fig.update_layout(width=800, height=400)
        st.write(fig)


