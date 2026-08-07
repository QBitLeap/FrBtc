# Fractal Bitcoin Node for Umbrel

A standalone, pruned Fractal Bitcoin node packaged as an Umbrel Community App.

## Resources

- 2 CPU cores
- 4 GB RAM recommended during initial sync
- Approximately 300 GB storage in mining-oriented prune mode
- `linux/amd64` only in the initial release

The app pins the official Fractald `v0.3.0` binary release, keeps RPC private,
and exposes Fractal's peer-to-peer port `8333` on the Umbrel host.

## Configuration

The managed configuration uses:

```ini
server=1
prune=30000
txindex=0
dbcache=1024
maxmempool=150
```

Data persists in `${APP_DATA_DIR}/data/fractal`.

## Local validation

```sh
python3 -m unittest -v fractal-node/dashboard/test_server.py
docker compose -f fractal-node/docker-compose.yml config
```

## Upstream

- Release repository: https://github.com/fractal-bitcoin/fractald-release
- Source repository: https://github.com/fractal-bitcoin/fractal
- Pinned release: `v0.3.0`

## License

The Umbrel packaging and dashboard in this repository are licensed under MIT.
Fractald is distributed by the Fractal Bitcoin project under its own license.
