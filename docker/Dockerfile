ARG UV_VERSION="0.12.3"
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM ubuntu:24.04

ARG TREPOGENO_URL="https://github.com/sanger-pathogens/trepogeno.git"
ARG TREPOGENO_TAG="v0.1.0"
ARG TREPOGENO_PATH="/opt/trepogeno"

ARG MCCORTEX_URL="https://github.com/Mykrobe-tools/mccortex.git"
ARG MCCORTEX_TAG="v0.0.5"

ARG PYTHON_VERSION="3.8"

ENV DEBIAN_FRONTEND=noninteractive

# install build dependencies
RUN apt-get update && \
    apt-get install -qq -y --no-install-recommends \
    git \
    make \
    gcc \
    g++ \
    zlib1g-dev \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /usr/local/bin/

WORKDIR ${TREPOGENO_PATH}

RUN git clone -q --depth 1 --recurse-submodules --branch ${TREPOGENO_TAG} ${TREPOGENO_URL} . && \
    cd trepogeno && \
    uv python install ${PYTHON_VERSION} && \
    uv venv --python ${PYTHON_VERSION} .venv && \
    uv pip install --python .venv -e . && \
    rm -rf .git && \
    cd src/trepogeno/mykrobe && \
    git clone -q --depth 1 --recurse-submodules --branch ${MCCORTEX_TAG} ${MCCORTEX_URL} mccortex && \
    cd mccortex && \
    make -s && \
    cp bin/mccortex31 ../src/mykrobe/cortex/ && \
    uv cache clean

ENV PATH="${TREPOGENO_PATH}/trepogeno/.venv/bin:${TREPOGENO_PATH}:${PATH}"