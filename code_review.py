import os

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


file_contents = {}
file_extensions = [".ipynb", ".py"]

def get_file_contents(path='.'):
    for filename in sorted((f for f in os.listdir(path) if not f.startswith(".")), key=str.lower):
        full_path = os.path.join(path, filename)
        if os.path.isdir(full_path):
            get_file_contents(full_path)
        else:
            _, file_extension = os.path.splitext(filename)
            if any(substring in file_extension for substring in file_extensions):
                    with open(full_path) as f: 
                        file_contents.update({filename: f.read()})


def drop_current_file(file_contents):
    current_filename = os.path.basename(__file__)
    file_contents.pop(current_filename, None)
    return file_contents


# Get a dictionary of all files in the current directory and subdirectories
get_file_contents()
# Drop the current file from the dictionary
drop_current_file(file_contents)

print(f"Found the following files: {list(file_contents.keys())}")

try:
    os.environ["AZURE_OPENAI_API_KEY"]
except Exception as e:
    print(f"No AZURE_OPENAI_API_KEY environment variable was found: {e}")

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",
    api_version="2024-02-01",
    temperature=0.7,
    max_tokens=250,
    timeout=None,
    max_retries=2,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a friendly {language} expert great at performing code reviews and editing code.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm

def run_ai_model(filename):
    ai_msg = chain.invoke(
        {
            "language": "Python",
            "input": f"Edit this script to make it easier to read, cleaner, and more reproducible. Add comments where necessary: {file_contents[filename]}",
        }
    )

    with open(f"llm_review/{filename}", "w") as file:
        print(f"Writing the edited file to llm_review/{filename}")
        file.write(ai_msg.content)


for filename in file_contents:
    run_ai_model(filename)
