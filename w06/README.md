# W06 Docker Lab

## Image Composition
- Layers: each Dockerfile instruction creates a cached layer
- Config: runtime settings (CMD, ENV, WORKDIR)
- Manifest: metadata describing image layers

---

## CMD vs ENTRYPOINT
See experimental results in Dockerfile.cmd-* files.

---

## Build Cache
v2 improves caching by separating dependency install from code copy.

---

## Multi-stage
Reduces build dependencies using builder stage.

---

## .dockerignore
Reduces build context size.

---

## Design decision
Used python:3.12-slim for balance of compatibility and size.
