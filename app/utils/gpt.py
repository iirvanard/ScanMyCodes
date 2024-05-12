import openai
import os


class CodeAnalyzer:

    def __init__(self, model=None):
        openai.api_key = os.getenv('OPENAI_KEY')
        openai.base_url = os.getenv('OPENAI_BASE_URL')
        self.model = model or "pai-001"

    def analyze_code_vulnerabilities(self, code, language=None):

        message_text = [{
            "role":
            "system",
            "content":
            "Use ```thisisthelanguage to put the completed code, including the necessary imports, in markdown quotes:\n{code} "
        }, {
            "role":
            "user",
            "content":
            f"Please analyze the following \n```{language}\n{code} code and provide any vulnerabilities, and report the vulnerability description, remediation, and reference and other impact details.\n "
        }]

        print(message_text)
        completion = openai.chat.completions.create(
            model=self.model,
            messages=message_text,
            temperature=0,
            n=1,
        )
        # Dapatkan output dari respons
        output_with_newlines = completion.choices[0].message.content.strip()

        return output_with_newlines
