import openai

openai.api_key  = "codellama"

openai.base_url = "http://localhost:11434/v1/"


language = "python"
code = """eval(input("Masukkan kode Python: "))"""

message_text = [{
         "role":
        
            "user",
            "content":
            f"I would like you to analyze the following code for security vulnerabilities. Identify vulnerabilities and provide a detailed report in the following format:\n**Vulnerability category**: includes owasp top 10 or cwe top 25\n**Description**: describes the vulnerability, including potential impacts or exploits.\n**Code that Affected**: sync line or section of code that caused the vulnerability.\n**other vulnerabilities**: if any other vulnerabilities are discovered\n**Remediation**: Provide specific steps to fix the vulnerability.\n** References**: Include resources or related documentation for more information add the url too.\nCode to be explained :\n{language}\n{code}"
        }]
completion = openai.chat.completions.create(
            model="codellama",
            messages=message_text,
            temperature=0,
            n=1,
        )
print(completion.choices[0].message.content)
