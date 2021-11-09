FROM jenkins/jenkins:2.303.3

# Docker install
USER root
RUN apt update && apt install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    ; \
    rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://download.docker.com/linux/debian/gpg |\
    gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/debian $(lsb_release -cs) stable" |\
    tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt update && apt install -y docker-ce-cli && rm -rf /var/lib/apt/lists/*

USER jenkins
