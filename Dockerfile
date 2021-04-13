FROM buildpack-deps:bionic-curl

ENV LC_ALL C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
    apt update; \
    apt-get -y install --no-install-recommends \
    git \
    git-lfs\
    libssl-dev \
    build-essential \
    default-libmysqlclient-dev \
    libsqlite3-dev \
    libbz2-dev \
    xz-utils \
    zlib1g-dev \
    gcc \
    vim \
    ; \
    rm -rf /var/lib/apt/lists/*;

ENV PYTHONUNBUFFERED=1

WORKDIR /

RUN wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz && tar -Jxvf Python-3.6.3.tar.xz && rm Python-3.6.3.tar.xz
RUN cd /Python-3.6.3/ && \
    ./configure --with-ssl && make && make install && \
    cd / && rm -rf Python-3.6.3/

COPY requirements.txt .

RUN pip3 install --no-cache-dir -U pip && \
    pip3 install --no-cache-dir -r requirements.txt

WORKDIR /flowlab
