class ErrorHandler:
    error_messages = {
        'en': {
            'internal_error':
            "Internal server error. Please try again later.",
            'not_found':
            "Page not found. The requested page cannot be found.",
            'incorrect_email_password':
            "Email or password is incorrect! Please check your credentials and try again.",
            'email_already_registered':
            "Email is already registered. Please use a different email.",
            'invalid_email_format':
            "Invalid email format. Please enter a valid email address.",
            'password_too_weak':
            "Password is too weak. Please choose a stronger password."
        },
        'id': {
            'internal_error':
            "Kesalahan server internal. Silakan coba lagi nanti.",
            'not_found':
            "Halaman tidak ditemukan. Halaman yang diminta tidak dapat ditemukan.",
            'incorrect_email_password':
            "Email atau kata sandi salah! Mohon periksa kredensial Anda dan coba lagi.",
            'email_already_registered':
            "Email sudah terdaftar. Silakan gunakan email lain.",
            'invalid_email_format':
            "Format email tidak valid. Mohon masukkan alamat email yang valid.",
            'password_too_weak':
            "Kata sandi terlalu lemah. Mohon pilih kata sandi yang lebih kuat."
        }
    }

    @staticmethod
    def get_error_message(error, lang='en'):
        return ErrorHandler.error_messages[lang].get(
            error, ErrorHandler.error_messages[lang]['internal_error'])
