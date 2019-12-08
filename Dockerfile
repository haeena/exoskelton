FROM python:3.8

ARG TINI_VERSION=v0.18.0
RUN curl -fsSL https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-static-$(dpkg --print-architecture) -o /sbin/tini \
    && curl -fsSL https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-static-$(dpkg --print-architecture).asc -o /sbin/tini.asc \
    && gpg --batch --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7 \
    && gpg --batch --verify /sbin/tini.asc /sbin/tini \
    && rm -rf /sbin/tini.asc /root/.gnupg \
    && chmod +x /sbin/tini

WORKDIR /usr/src/exoskelton
COPY . .

COPY pyproject.toml ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir . \
    && pip install --no-cache-dir ptvsd

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python", "-m", "exoskelton.run"]
