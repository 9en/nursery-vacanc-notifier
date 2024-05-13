FROM python:3.11

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV PYTHONPATH="${PYTHONPATH}:/app/function"

WORKDIR /app

COPY entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]