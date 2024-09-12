import streamlit as st

from back import read_files

st.title('Generate code documentation')

st.write('Use LLMs to generate documentation, annotations and docstrings for your code.')

files = st.file_uploader(
    label='**Upload your documents**',
    key='code_files',
    accept_multiple_files=True,
)

if files:
    st.write(read_files(files))
