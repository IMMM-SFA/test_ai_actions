import os

from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


try:
    # This code will raise a NameError because 'my_variable' is not defined
    os.environ["AZURE_OPENAI_API_KEY"]
except Error as e:
    # This block will execute if an Error occurs
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
chain.invoke(
    {
        "language": "Python",
        "input": "Go through all the scripts in this repository and provide detailed feedback and suggestions on how to make the scripts easier to read, cleaner, and more reproducible.",
    }
)

print(chain)