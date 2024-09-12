import io
import json
import os
import zipfile

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=API_KEY)

with open('prompts.json', 'r') as f1:
    PROMPTS = json.load(f1)

with open('file_extensions.json', 'r') as f2:
    FILE_EXTENSIONS = json.load(f2)

file_extensions_dict = {
    ext.replace('.', ''): data['name']
    for data in FILE_EXTENSIONS
    for ext in data.get('extensions', [])
}


def unzip(zip_file):
    zip_file = zipfile.ZipFile(zip_file)
    return {name: zip_file.read(name) for name in zip_file.namelist()}


def read_files(files: list):
    file_data = []
    for file in files:
        file_extension = file.name.rsplit('.')[-1] if '.' in file.name else ''
        if file_extension:
            stringio = io.StringIO(file.getvalue().decode("utf-8"))
            code = stringio.read()
            language = file_extensions_dict.get(file_extension, '')
            language_md = language.lower()  # NOTE: por mientras
            file_data.append(
                {
                    'file_name': file.name,
                    'code': code,
                    'language': language,
                    'language_md': language_md,
                }
            )
    return file_data


def generate_text(input_text: str) -> tuple[str, bool]:
    response = client.chat.completions.create(
        model='gpt-4o',
        temperature=0.0,
        messages=[{'role': 'user', 'content': input_text}],
        stream=False,
    )
    finish = response.choices[0].finish_reason == 'stop'
    response_text = response.choices[0].message.content
    response_text = response_text if response_text else ''
    return (response_text, finish)


def annotate_code(file_data: dict, run_limit: int = 5) -> str:
    finish, n_runs = False, 0
    doc_prompt, doc_cont_prompt = PROMPTS
    while not finish and n_runs < run_limit:
        pass


def save_in_memory(rendered_text: str) -> io.BytesIO:
    """
    Save rendered text as bytes in memory.

    Args:
        rendered_text (str): Rendered template text.

    Returns:
        io.BytesIO: BytesIO object containing the rendered text.
    """
    file_bytes = io.BytesIO()
    file_bytes.write(rendered_text.encode())
    file_bytes.seek(0)
    return file_bytes


def create_zip_archive(files: list[tuple[io.BytesIO, str]]) -> io.BytesIO:
    """
    Create a zip archive containing the generated files.

    Args:
        files (list[tuple[io.BytesIO, str]]): List of tuples containing file bytes and filenames.

    Returns:
        io.BytesIO: BytesIO object containing the zip archive.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zip_file:
        for file_bytes, filename in files:
            zip_file.writestr(filename, file_bytes.getvalue())
    zip_buffer.seek(0)
    return zip_buffer
