
import streamlit as st
from pathlib import Path
import os
import glob
import pandas as pd
import textract as tx
import fileReader
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib_venn_wordcloud import venn2_wordcloud

def match_skills(rs_skillset, jd_skillset,jd_name):
    if len(jd_skillset) < 1:
        print('could not extract skills from job offer text')
    else:
        pct_match = round(len(rs_skillset.intersection(jd_skillset)) / len(rs_skillset) * 100, 0)
        return (jd_name, pct_match,list(jd_skillset))
@st.cache
def executeSingle(parent_path,save_path):
    Jobs = pd.read_csv(os.path.join(parent_path, 'Job_Data.csv'))
    jd_skillset_dict = {}
    for i in range(len(Jobs['Name'])):
        jd_skillset_dict[Jobs['Name'][i]] = (Jobs['Entities'][i]).split(",")
    text = tx.process(save_path, encoding='ascii')
    text = str(text, 'utf-8')
    rs_skillset = fileReader.getEntities(text)
    match_pairs = [match_skills(set(rs_skillset), set(jd_skillset_dict[name]), name) for name in jd_skillset_dict.keys()]
    return [rs_skillset,match_pairs]


if (not st.session_state["authentication_status"]) or (not st.session_state["st_user"]):
    st.write('Please login')
    st.stop()
else:
    us = ""

    if 'st_user' in st.session_state:
        us = st.session_state['st_user']
    parent_path = os.path.join(os.getcwd(), 'data', us)
    trash_folder = os.path.join(parent_path, 'trash','temp')
    os.makedirs(trash_folder, exist_ok=True)
    st.title("Upload Resume to get Recomandations")
    # st.image(res, width = 800)
    with st.form(key="Form :", clear_on_submit=True):
        File = st.file_uploader(label="Upload file", type=["pdf", "docx", "txt"], accept_multiple_files=True)
        Submit = st.form_submit_button(label='Submit')

    if Submit:
        st.markdown("*The file is sucessfully Uploaded.*")
        import shutil

        shutil.rmtree(trash_folder)
        for File in File:
            save_path = Path(trash_folder, File.name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, mode='wb') as w:
                w.write(File.getvalue())
            if save_path.exists():
                st.success(f'File {File.name} is successfully saved!')
    if not os.path.isfile(os.path.join(parent_path, 'Job_Data.csv')):
        st.markdown("There is no Job profiles uploaded to compare")
        st.stop()
    if len(os.listdir(trash_folder))==0:
        st.stop()
    res_path=os.path.join(trash_folder,os.listdir(trash_folder)[0])
    print(res_path)
    rs_skill,match_pair=executeSingle(parent_path,res_path)
    print("rs_skill")
    print(rs_skill)
    print("match_pair")
    print(match_pair)

    finn=[]
    cv_entities_dic={}
    for i in range(len(match_pair)):
        finn.append([match_pair[i][0],match_pair[i][1]])
        cv_entities_dic[match_pair[i][0]]= match_pair[i][2]
    chart_data = pd.DataFrame(
        finn,columns=["Name", "Scores"])

    chart_data = chart_data.sort_values(
        by=['Scores'], ascending=False).reset_index(drop=True)

    chart_data['Rank'] = pd.DataFrame(
        [i for i in range(1, len(chart_data['Scores']) + 1)])
    fig2 = px.bar(chart_data,
                  x=chart_data['Name'], y=chart_data['Scores'], color='Scores',
                  color_continuous_scale='haline', title="Cv vs JD scores")

    st.plotly_chart(fig2, use_container_width=True)

    sel_jd = st.selectbox("Select JD ", options=cv_entities_dic.keys())
    if(len(set(rs_skill).intersection(set(cv_entities_dic[sel_jd])))==0):
        st.markdown("There is no match in features in resume with '"+sel_jd+"' Job profile")
        st.stop()
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title("Venn digram for Job features Vs resume", fontsize=20)
    v = venn2_wordcloud([set(rs_skill), set(cv_entities_dic[sel_jd])],
                        ax=ax, set_labels=["Cv Features", "JD :" + sel_jd])
    # add color
    v.get_patch_by_id("10").set_color("red")
    v.get_patch_by_id("10").set_alpha(0.4)
    v.get_patch_by_id("01").set_color("blue")
    v.get_patch_by_id("01").set_alpha(0.4)
    v.get_patch_by_id("11").set_color("purple")
    v.get_patch_by_id("11").set_alpha(0.4)
    st.pyplot(fig)
