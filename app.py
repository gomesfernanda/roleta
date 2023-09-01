import datetime
import random
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#########################
#                       #
#   AUTHORIZE GOOGLE    #
#                       #
#########################

@st.cache_resource
def authorize_google_api(sheet, worksheet):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    json_data = {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"],
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_data)
    gc = gspread.authorize(credentials)
    auth = gc.open(sheet).worksheet(worksheet)
    return auth

def get_tasks(auth, tempo):
    all_values = auth.get_all_values()
    tasks = all_values[1:]
    tarefasdict = {item[0]: item[1:] for item in tasks if item[4] == "" if item[2] == tempo}
    tarefasnome = [item[0] for item in tarefasdict.values()]
    return tarefasdict, tarefasnome

def pick_task(task_dict):
    sortearlist = list(task_dict.keys())
    n = random.randint(0, len(sortearlist) - 1)
    task = task_dict[sortearlist[n]][0]
    minutes = task_dict[sortearlist[n]][1]
    key = sortearlist[n]
    return key, task, minutes

def add_task_sheet(auth, task, duration):
    today = datetime.date.today()
    today = today.strftime('%d/%m/%Y')
    row = auth.cell(1, 6).value
    auth.update_cell(row, 2, task)
    auth.update_cell(row, 3, duration)
    auth.update_cell(row, 4, today)
    return row

def complete_task_sheet(auth, taskrow):
    today = datetime.date.today()
    today = today.strftime('%d/%m/%Y')
    compl = int(taskrow) + 1
    auth.update_cell(compl, 5, today)

def main():
    sheet = st.secrets['sheet']
    worksheet = st.secrets['worksheet']
    auth = authorize_google_api(sheet, worksheet)

    st.title('Roleta das tarefas')  # Set Title of the webapp
    st.image('https://media4.giphy.com/media/70OiJhMBae5j6AFL3f/200w.webp?cid=ecf05e47w34ilvp46d7uz4sjs06tl8p87tuq6zumcxubwuoa&ep=v1_gifs_related&rid=200w.webp&ct=g')
    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    def set_state(i):
        st.session_state.stage = i

    def set_complete(i, row):
        st.session_state.stage = i
        complete_task_sheet(auth, row)

    def set_state_18():
        st.session_state.text = ""
        st.session_state.stage = -1

    def clear_text():
        st.session_state["text1"] = ""
        st.session_state["text2"] = ""

    if st.session_state.stage == 0:
        st.button('Sortear e completar', on_click=set_state, args=[1])
        st.button('Adicionar', on_click=set_state_18)

    if st.session_state.stage == -1:
        st.header('Nova tarefa')
        task = st.text_input('Descrição', key='text1')
        duration = st.selectbox(
            'Quanto tempo irá durar aproximadamente?',
            ('', 'Pouco', 'Médio', 'Bastante'), placeholder='Selecione', key='text2')
        duration = duration.lower()
        if st.button('Salvar'):
            add_task_sheet(auth, task, duration)
            st.write('Tarefa ' + task.upper() + ' salva')
        st.button('Adicionar outra', on_click=clear_text)
        st.button('Tela inicial', on_click=set_state, args=[0])

    if st.session_state.stage >= 1 and st.session_state.stage != 10:
        tempo = st.radio(
            "Quanto tempo você tem?",
            ["↓", "Pouco", "Médio", "Bastante"], on_change=set_state, args=[2])

    if st.session_state.stage >= 2 and st.session_state.stage != 10:
        st.header('Tarefas disponíveis')
        tdict, tname = get_tasks(auth, tempo.lower())
        s = ''
        for i in tname:
            s += "- " + i + "\n"
        st.markdown(s)
        if st.button('Sortear tarefa'):
            n, tasksel, tempo = pick_task(tdict)
            st.header('Tarefa sorteada:')
            st.write(tasksel)
            st.button('Tarefa completa', on_click=set_complete, args=[10, n])
            st.button('Tela inicial', on_click=set_state, args=[0])

    if st.session_state.stage == 10:
        st.write('PARABÉNS!')
        st.image('https://media0.giphy.com/media/jJQC2puVZpTMO4vUs0/200.webp?cid=ecf05e47vyst9gc7c9cyfkxcttb556xw402juhd0yunoeeyn&ep=v1_gifs_search&rid=200.webp&ct=g')
        st.button('Sortear novamente', on_click=set_state, args=[1])
        st.button('Tela inicial', on_click=set_state, args=[0])

if __name__ == '__main__':
    main()

