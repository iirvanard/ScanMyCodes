import openai
import os
import re
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
class CodeAnalyzer:

    def __init__(self, model=None):



        # openai.api_key = "codellama"
        # openai.base_url = "http://localhost:11434/v1/"
        # self.model = "codellama"
        
        # openai.api_key = "codellama"
        # openai.base_url = "http://localhost:11434/v1/"
        # self.model = "codellama"

        openai.api_key = "zu-06070bedc39a7b0f9a16f87c6addec75"
        openai.base_url = "https://api.zukijourney.com/v1/"
        self.model = "gemini-1.5-pro-latest"

    def analyze_code_vulnerabilities(self, code, language=None):

        message_text = [{
            "role":
            "system",
            "content":"dalam bahasa indonesia",
            "role":
            "user",
            "content":
            f"Saya ingin Anda menganalisis kode berikut untuk kerentanan keamanan. Identifikasi kerentanan dan berikan detail laporan dengan format berikut:\n**kategori Kerentanan**: termasuk owasp top 10 atau cwe top 25\n**Deskripsi**: Jelaskan kerentanan, termasuk dampak atau eksploitasi potensial.\n**Kode yang Terpengaruh**: Sebutkan baris atau bagian kode yang menyebabkan kerentanan.\n**kerentanan lainnya**: jika terdapat kerentanan lain yang ditemukan\n**remidisi**: Berikan langkah-langkah spesifik untuk memperbaiki kerentanan tersebut.\n**Referensi**: Sertakan sumber daya atau dokumentasi terkait untuk informasi lebih lanjut.\nKode yang akan dianalisis:\n{language}\n{code}"
        }]

        completion = openai.chat.completions.create(
            model=self.model,
            messages=message_text,
            n=1,
        )
        return (completion.choices[0].message.content)
    
