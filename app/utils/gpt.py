import openai
import os
import re


class CodeAnalyzer:

    def __init__(self, model=None):
        openai.api_key = os.getenv('OPENAI_KEY')
        openai.base_url = os.getenv('OPENAI_BASE_URL')
        # openai.base_url = "asdasd"
        self.model = model or "pai-001"

    def analyze_code_vulnerabilities(self, code, language=None):

        message_text = [{
            "role":
            "user",
            "content":
            f"Please analyze the following \n```{language}\n{code} code and provide any vulnerabilities, and report the vulnerability details such Description,Remediations,References .\n "
        }]

        print(message_text)
        completion = openai.chat.completions.create(
            model=self.model,
            messages=message_text,
            temperature=0,
            n=1,
        )
     
        return completion.choices[0].message.content
    

