# Fractal Bitcoin Node for Umbrel

A standalone, pruned Fractal Bitcoin node packaged as an Umbrel Community App.

## Resources

- 2 CPU cores
- 4 GB RAM recommended during initial sync
- 2,000 MiB raw block and undo-data pruning target, plus chainstate and
  block-index storage; this retains headroom above Fractald's 550 MiB minimum
- `linux/amd64` only in the initial release

The app pins the official Fractald `v0.3.0` binary release and keeps RPC
private. Fractald makes outbound peer connections without claiming Bitcoin
Node's host port `8333`.

## Configuration

The managed configuration uses:

```ini
server=1
prune=2000
txindex=0
dbcache=1024
maxmempool=150
```

Data persists in `${APP_DATA_DIR}/data/fractal`.

The dashboard stores its last successful RPC snapshot separately. During a
short RPC timeout caused by intensive initial-sync validation, it continues to
show the last verified height and progress as `Synchronizing (RPC busy)` rather
than resetting the display to `Starting`.

## Local validation

```sh
(cd qbitleap-frbtc-fractal-node/dashboard && python3 -m unittest -v test_server.py)
docker compose -f qbitleap-frbtc-fractal-node/docker-compose.yml config
```

## Upstream

- Release repository: https://github.com/fractal-bitcoin/fractald-release
- Source repository: https://github.com/fractal-bitcoin/fractal
- Pinned release: `v0.3.0`

The scheduled release workflow checks for a newer stable Fractald release each
week. It validates the GitHub-provided asset digest, runs dashboard and Compose
tests, builds the candidate images, and exercises the node's regtest RPC. The
Umbrel version is bumped and pushed only after every compatibility gate passes.

## License

The Umbrel packaging and dashboard in this repository are licensed under MIT.
Fractald is distributed by the Fractal Bitcoin project under its own license.
