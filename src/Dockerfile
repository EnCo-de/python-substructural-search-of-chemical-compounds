# Environment build stage
FROM continuumio/miniconda3 AS build
RUN conda install -c conda-forge  --yes conda-pack

# Create the conda environment using environment.yml file
COPY environment.yml .
RUN conda env create -f environment.yml && \
  conda clean --all --yes && pip cache purge && rm -rf /tmp/*

# Package the environment as tar using conda-pack
RUN conda-pack -n slim -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar -xf /tmp/env.tar && \
  rm /tmp/env.tar
RUN /venv/bin/conda-unpack


# Runtime stage

# using slim debian image as the base image for the environment copy the environment directory from the build stage
FROM debian:12.6-slim AS runtime
COPY --from=build /venv /venv
SHELL ["/bin/bash", "-c"]

WORKDIR /src
EXPOSE 8000
COPY . /src
ENTRYPOINT source /venv/bin/activate && \
                    uvicorn main:app --host 0.0.0.0 --port 8000
CMD [ "--proxy-headers"]