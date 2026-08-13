FROM ubuntu:24.04

ARG TREPOGENO_URL="https://github.com/sanger-pathogens/trepogeno.git"
# TODO: ARG TREPOGENO_TAG=""
ARG TREPOGENO_PATH="/opt/trepogeno"
ARG MCCORTEX_URL="https://github.com/Mykrobe-tools/mccortex.git"
ARG MCCORTEX_TAG="v0.0.5"

ENV DEBIAN_FRONTEND=noninteractive

# install build dependencies
RUN apt-get update && \
    apt-get install -qq -y --no-install-recommends \
    git \
    python3-pip \
    make \
    gcc \
    g++ \
    zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR ${TREPOGENO_PATH}

# clone the repo (and its Mykrobe submodule) and install
RUN git clone --recurse-submodules --branch ${TREPOGENO_TAG} ${TREPOGENO_URL} . && \
    cd ./trepogeno/ && \
    pip3 install --break-system-packages -e . &&\
    cd src/trepogeno/mykrobe && \
    git clone --recurse-submodules --branch ${MCCORTEX_TAG} ${MCCORTEX_URL} mccortex && \
    cd mccortex && \
    make && \
    cp bin/mccortex31 ../src/mykrobe/cortex/
    # TODO: add cleanup

ENV PATH="${TREPOGENO_PATH}:${PATH}"