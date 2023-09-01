import streamlit as st

st.title('Greatest of Three Numbers') # Set Title of the webapp

choice1 = st.number_input('Enter First number') #Accepts a number input
choice2 = st.number_input('Enter Second number')
choice3 = st.number_input('Enter Third number')

string = f'Maximum value is {max(choice1,choice2,choice3)}'

st.write(string)
