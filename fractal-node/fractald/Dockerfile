# syntax=docker/dockerfile:1.7

FROM debian:bookworm-slim

ARG FRACTALD_VERSION=0.3.0
ARG FRACTALD_ARCHIVE=fractald-0.3.0-x86_64-linux-gnu.tar.gz
ARG FRACTALD_SHA256=0321234913e3543cda1c6c07163ac5c3b259b1ce26118ee21e930fd9b48f9d5b

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl --proto '=https' --tlsv1.2 --fail --location \
      --output /tmp/fractald.tar.gz \
      "https://github.com/fractal-bitcoin/fractald-release/releases/download/v${FRACTALD_VERSION}/${FRACTALD_ARCHIVE}" \
    && echo "${FRACTALD_SHA256}  /tmp/fractald.tar.gz" | sha256sum --check --strict \
    && tar -xzf /tmp/fractald.tar.gz -C /tmp \
    && install -m 0755 "/tmp/fractald-${FRACTALD_VERSION}-x86_64-linux-gnu/bin/bitcoind" /usr/local/bin/bitcoind \
    && install -m 0755 "/tmp/fractald-${FRACTALD_VERSION}-x86_64-linux-gnu/bin/bitcoin-cli" /usr/local/bin/bitcoin-cli \
    && rm -rf /tmp/fractald.tar.gz "/tmp/fractald-${FRACTALD_VERSION}-x86_64-linux-gnu"

RUN useradd --create-home --uid 1000 fractal \
    && mkdir -p /data /config \
    && chown -R fractal:fractal /data /config

USER fractal
EXPOSE 8332 8333
ENTRYPOINT ["bitcoind"]
