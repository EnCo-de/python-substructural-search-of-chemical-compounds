FROM continuumio/miniconda3
RUN conda install conda-forge::rdkit && \
       conda clean -afy
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt && pip freeze
WORKDIR /src
EXPOSE 8000
COPY . /src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]