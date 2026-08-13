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
    make \
    gcc \
    g++ \
    zlib1g-dev \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /uvx /usr/local/bin/

WORKDIR ${TREPOGENO_PATH}

RUN git clone --recurse-submodules --branch ${TREPOGENO_TAG} ${TREPOGENO_URL} . && \
    cd trepogeno && \
    uv python install 3.8 && \
    uv venv --python 3.8 .venv && \
    uv pip install --python .venv -e . && \
    cd src/trepogeno/mykrobe && \
    git clone --recurse-submodules --branch ${MCCORTEX_TAG} ${MCCORTEX_URL} mccortex && \
    cd mccortex && \
    make && \
    cp bin/mccortex31 ../src/mykrobe/cortex/
    # TODO: add cleanup

ENV PATH="${TREPOGENO_PATH}/trepogeno/.venv/bin:${TREPOGENO_PATH}:${PATH}"