FROM continuumio/miniconda3
RUN conda install conda-forge::rdkit
RUN conda install -y conda-forge::fastapi conda-forge::uvicorn
# FROM python:3.12
WORKDIR /code
# COPY ./requirements.txt /code/requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./src /code/src
CMD ["fastapi", "run", "src/main.py", "--port", "80"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]