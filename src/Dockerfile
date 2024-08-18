FROM python:3.12.5-slim
WORKDIR /src
COPY requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir -r /src/requirements.txt  && \
    pip cache purge && rm -rf /tmp/*
EXPOSE 8000
COPY . /src
ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8000
CMD ["--proxy-headers"]

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
