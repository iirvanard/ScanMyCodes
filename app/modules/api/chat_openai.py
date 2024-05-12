from flask import Blueprint, jsonify, request
from app.utils.gpt import CodeAnalyzer
from app.extensions import csrf
from werkzeug.exceptions import BadRequest

blueprint = Blueprint('api', __name__, url_prefix='/api')

ChatGpt = CodeAnalyzer()


# Fungsi untuk membuat respons API
def make_response(status_code, message=None, data=None):
    response = {"status_code": status_code, "message": message, "data": data}
    return jsonify(response), status_code


# Endpoint untuk chatgpt
@blueprint.route('/chat', methods=['POST'])
@csrf.exempt
def chat():
    try:
        # Memeriksa apakah data JSON diterima dan formatnya benar
        json_data = request.get_json()
        if not json_data or 'source_code' not in json_data:
            raise BadRequest("Invalid request data")

        # Mendapatkan bahasa dan kode sumber dari data JSON
        language = json_data.get('language')
        source_code = json_data.get('source_code')

        # Memeriksa apakah bahasa atau kode sumber kosong
        if not source_code:
            raise BadRequest(" source code cannot be empty")

        # Menjalankan analisis kerentanan kode
        prompt_chat = ChatGpt.analyze_code_vulnerabilities(
            source_code, language)

        # Mengembalikan respons dengan data yang dianalisis
        return make_response(200, 'Success retrieved data', prompt_chat)

    except BadRequest as e:
        return make_response(e.code, str(e.description))

    except Exception as e:
        # Menangani kesalahan internal server
        return make_response(500, str(e))
    # return {
    #     "data":
    #     "## Vulnerability Analysis: `file_get_contents()` with Suppression of Errors using the @-sign\n\nThe provided code snippet uses the PHP function `file_get_contents()` to read a file from a given URL, and suppresses any potential errors by prefixing it with an at-sign (`@`) symbol. This technique is called **error suppression**. In this case, if the function call fails due to various reasons such as network issues or unreachable URLs, no error message will be displayed. Instead, the script will simply move on to execute the next line of code following this statement without raising any warning or noticeable indication that an error has occurred.\n\n## Vulnerability Description: Potential for Hidden Errors and Lack of Visibility into System Behavior\nError suppression can lead to hidden errors in your application logic which may not be easily detectable during development or testing phases. These hidden errors could potentially cause unexpected behavior downstream in your system when triggered under specific conditions like user input validation failures or external dependencies becoming unavailable. By ignoring these warnings and exceptions through error suppression techniques like shown above, you are essentially turning off important feedback mechanisms that help developers understand their applications' behavior better and maintain them more effectively over time. Moreover, debugging becomes much harder since there won't be any visible trace left behind indicating where things went wrong initially. \n<br>**Recommendation:** It is generally considered best practice not to use error suppression unless absolutely necessary (e.g., for performance optimization purposes). Instead, handle exceptions gracefully within your codebase so that users receive meaningful messages explaining what happened instead of encountering cryptic errors or blank screens.***</br>Instead of using `@file_get_contents($url)`, consider wrapping it inside a try/catch block as follows: ```php <?php try { $content = file_get_contents($url); } catch(Exception $e) { // Handle exception here } ?> ``` This way you can log appropriate messages based on different types of exceptions thrown by PHP functions like `file_get_contents()`. Additionally, make sure proper HTTP headers are set according to content type returned by remote server while fetching data via cURL or other similar methods if needed.\" </p> \n### Impact Details: - Increased risk for security vulnerabilities due to lack of visibility into system behavior - Difficulty in debugging",
    #     "message": "Success retrieved data",
    #     "status_code": 200
    # }
