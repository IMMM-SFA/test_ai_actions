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


get_file_contents()
print(f"Found the following files: {list(file_contents.keys())}")

try:
    os.environ["AZURE_OPENAI_API_KEY"]
except Error as e:
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
            "You are a friendly {language} expert performing a code review to provide helpful feedback to the programmer.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm
ai_msg = chain.invoke(
    {
        "language": "Python",
        "input": f"Go through all the scripts in the following dictionary of scripts and provide detailed feedback and suggestions on how to make the scripts easier to read, cleaner, and more reproducible. Provide specific examples and reference code blocks: {file_contents}",
    }
)

print(ai_msg.content)