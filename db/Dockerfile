FROM python:3.9-slim
WORKDIR /app
RUN pip install flask requests psycopg2-binary
COPY app.py .
EXPOSE 80
CMD ["python", "app.py"]