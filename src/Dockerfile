FROM python:3.12.5-slim
WORKDIR /src
RUN python3 -m pip install --upgrade pip
COPY requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir -r /src/requirements.txt
EXPOSE 5000
COPY . /src
ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 5000
CMD ["--proxy-headers"]
