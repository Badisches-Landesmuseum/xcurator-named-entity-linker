# https://hub.docker.com/_/ubuntu
FROM ubuntu:22.04

# Expose port for Docker (our default for microservices is 80)
EXPOSE 80

# Create a non-root user
ARG username=app
ARG uid=1000
ARG gid=100
ENV USER ${username}
ENV UID ${uid}
ENV GID ${gid}
ENV HOME /home/${UID}
RUN adduser --disabled-password --gecos "Non-root user" --uid ${UID} --gid ${GID} --home ${HOME} ${USER}

# Inject conda packages by the CI/CD pipeline to run 'conda create env' only once
ENV PATH /opt/conda/bin:$PATH
#ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/conda/lib
COPY /opt/conda/ /opt/conda/

COPY named_entities_service /named_entities_service

# change ownership so non-root can use files
RUN chown ${UID}:${GID} /opt/conda/ /named_entities_service

USER ${USER}

ENTRYPOINT ["python", "/named_entities_service"]
