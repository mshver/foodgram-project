FROM python:3.8.5
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY Slimamif.ttf /usr/share/fonts/truetype/
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]