# Gunakan Ubuntu versi terbaru sebagai base image
FROM ubuntu:latest
FROM python:3.11
# Informasi tentang pembuat (Opsional)
LABEL maintainer="IRVAN ARDIANSYAH <irvan9110@gmail.com>"


COPY . .
# Tentukan direktori kerja
WORKDIR /app

# Salin file-file dari host ke dalam image


COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

# Buka port 5000 untuk koneksi HTTP
EXPOSE 5000

# Jalankan aplikasi Flask ketika container dimulai
CMD ["flask", "run"]

# CMD [ "gunicorn", "-w", "4", "-b","0.0.0.0:5000","--reload","app:create_app('development')" ]
