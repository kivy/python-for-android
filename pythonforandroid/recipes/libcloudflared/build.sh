
#!/bin/sh
set -eu

: "${GO:?GO executable not supplied}"
: "${CC:?Android CC not supplied}"
: "${CXX:?Android CXX not supplied}"

mkdir -p libs/aarch64

echo "Go: $("$GO" version)"
echo "CC: $CC"
echo "CXX: $CXX"

export CGO_ENABLED=1
export GOOS=android
export GOARCH=arm64
export CC
export CXX

"$GO" build \
    -ldflags="-linkmode=external -extldflags=-Wl,-z,max-page-size=16384" \
    -o libs/aarch64/cloudflared-arm64 \
    ./cmd/cloudflared/

chmod 755 libs/aarch64/cloudflared-arm64

echo "Cloudflared Android ARM64 build completed"
