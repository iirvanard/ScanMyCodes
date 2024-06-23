import openai
import os
<<<<<<< HEAD
=======
import re
>>>>>>> 57a24e6 (before revisi)


class CodeAnalyzer:

    def __init__(self, model=None):
        openai.api_key = os.getenv('OPENAI_KEY')
        openai.base_url = os.getenv('OPENAI_BASE_URL')
<<<<<<< HEAD
=======
        # openai.base_url = "asdasd"
>>>>>>> 57a24e6 (before revisi)
        self.model = model or "pai-001"

    def analyze_code_vulnerabilities(self, code, language=None):

        message_text = [{
            "role":
<<<<<<< HEAD
            "system",
            "content":
            "Use ```thisisthelanguage to put the completed code, including the necessary imports, in markdown quotes:\n{code} "
        }, {
            "role":
            "user",
            "content":
            f"Please analyze the following \n```{language}\n{code} code and provide any vulnerabilities, and report the vulnerability description, remediation, and reference and other impact details.\n "
=======
            "user",
            "content":
            f"Please analyze the following \n```{language}\n{code} code and provide any vulnerabilities, and report the vulnerability details such Description,Remediations,References .\n "
>>>>>>> 57a24e6 (before revisi)
        }]

        print(message_text)
        completion = openai.chat.completions.create(
            model=self.model,
            messages=message_text,
            temperature=0,
            n=1,
        )
<<<<<<< HEAD
        # Dapatkan output dari respons
        output_with_newlines = completion.choices[0].message.content.strip()

        return output_with_newlines
=======
     
        return completion.choices[0].message.content
    

>>>>>>> 57a24e6 (before revisi)
