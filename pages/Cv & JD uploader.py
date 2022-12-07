import app
import streamlit as st
from pathlib import Path
import os
import glob


import fileReader

if (not st.session_state["authentication_status"] ) or (not st.session_state["st_user"] ):
    st.write('Please login')    
    st.stop()
else:
    us=""

    if 'st_user' in st.session_state:
        us=st.session_state['st_user']
    parent_path = os.path.join(os.getcwd(), 'data', us)
    os.makedirs(os.path.join(parent_path, 'Resumes'), exist_ok=True)
    os.makedirs(os.path.join(parent_path, 'JobDesc'), exist_ok=True)
    # import app
    # if not app.login_check:
    #     st.session_state.runpage = "app"
    #     st.session_state.runpage()
    #     st.experimental_rerun()
    # st.markdown("Upload Files")
    st.sidebar.markdown("Upload Files")
    st.title("Upload Resume")
    # st.image(res, width = 800)
    with st.form(key="Form :", clear_on_submit = True):
        File = st.file_uploader(label = "Upload file", type=["pdf","docx","txt"] ,accept_multiple_files=True)
        Submit = st.form_submit_button(label='Submit')

    if Submit :
        st.markdown("*The file is sucessfully Uploaded.*")
        for File in File:
            # Save uploaded file to 'F:/tmp' folder.
            #save_folder = 'E:/POI/ScraperBack/Data/Resumes'
            save_folder = os.path.join(parent_path, 'Resumes')
            print("Resumen path:"+save_folder)
            save_path = Path(save_folder, File.name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, mode='wb') as w:
                w.write(File.getvalue())
            if save_path.exists():
                st.success(f'File {File.name} is successfully saved!')
    st.title("Upload Job Description")
    # st.image(res, width = 800)
    with st.form(key="Form1 :", clear_on_submit = True):
        File = st.file_uploader(label = "Upload file", type=["pdf","docx","txt"] , accept_multiple_files=True)
        Submit1 = st.form_submit_button(label='Submit')
        
    if Submit1 :
        st.markdown("*The file is sucessfully Uploaded.*")
        for File in File:
            # Save uploaded file to 'F:/tmp' folder.
            #save_folder = 'E:/POI/ScraperBack/Data/JobDesc'
            save_folder = os.path.join(parent_path, 'JobDesc')
            save_path = Path(save_folder, File.name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, mode='wb') as w:
                w.write(File.getvalue())
            if save_path.exists():
                st.success(f'File {File.name} is successfully saved!')


    with st.form(key="Formfin :", clear_on_submit = True):
        col_jd1, col_jd2 = st.columns((1, 1))
        with col_jd1:
            res_purge_Submit = st.form_submit_button(label='Purge all existing resumes')
        with col_jd2:
            jd_purge_Submit = st.form_submit_button(label='Purge all existing Job Desciptions')
    if res_purge_Submit:
        # st.error("Do you really, really, wanna purge all the resumes?")
        # rs_bt=st.button("Yes I'm ready to lit to woods")
        # if rs_bt:
        res_folder = os.path.join(parent_path, 'Resumes')
        trash_folder = os.path.join(parent_path, 'trash')
        os.makedirs(trash_folder, exist_ok=True)
        files = glob.glob(res_folder + '/**/*.*', recursive=True)
        for f in files:
            st.text("R-Del : " + os.path.split(f)[1])
            os.replace(f,os.path.join( trash_folder,os.path.split(f)[1]))
        st.markdown("done, all resumes have been burned!!")
    if jd_purge_Submit:
        # st.error("Do you really, really, wanna purge all the resumes?")
        # rs_bt=st.button("Yes I'm ready to lit to woods")
        # if rs_bt:
        res_folder = os.path.join(parent_path, 'JobDesc')
        trash_folder = os.path.join(parent_path, 'trash')
        os.makedirs(os.path.dirname(trash_folder), exist_ok=True)
        files = glob.glob(res_folder + '/**/*.*', recursive=True)
        for f in files:
            st.text("J-Del : " + os.path.split(f)[1])
            os.replace(f,os.path.join( trash_folder,os.path.split(f)[1]))
        st.markdown("done, all Job Description's have been burned!!")
    res_names=None
    res_names=os.listdir(os.path.join(parent_path, 'Resumes'))
    res_options = st.multiselect(
        'Pleas select resumes for lab analysis',res_names,res_names)
    jd_names=None
    jd_names=os.listdir(os.path.join(parent_path, 'JobDesc'))
    jd_options = st.multiselect(
        'Pleas select job description for lab analysis',jd_names,jd_names)
    res_col, jd_col = st.columns((1, 1))
    with res_col:
        st.write('You selected resumes:', res_options)
    with jd_col:
        st.write('You selected JDs:', jd_options)

    with st.form(key="Formpro :", clear_on_submit = True):
        Submitpro = st.form_submit_button(label='Generate/process CSV files')
    if Submitpro :
        st.markdown("*Please wait*")
        with st.spinner('Wait for it...'):
            fileReader.execution(parent_path, res_options, jd_options)
        st.snow()
        st.markdown("done")


