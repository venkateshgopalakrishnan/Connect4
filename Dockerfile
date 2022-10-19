FROM python:3.10
 
WORKDIR /app
 
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir --upgrade -r /app/requirements.txt
COPY connect4 /app/connect4

EXPOSE 8080

USER 1000

CMD ["uvicorn", "connect4:app", "--host", "0.0.0.0", "--port", "8080"]
