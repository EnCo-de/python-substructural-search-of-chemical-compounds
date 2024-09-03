FROM python:3.12.5-slim
# WORKDIR /src
COPY requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir -r /src/requirements.txt
EXPOSE 8000
COPY . /src/
# RUN python3 create_table.py
ENTRYPOINT uvicorn src.main:app --host 0.0.0.0 --port 8000
CMD ["--proxy-headers"]
