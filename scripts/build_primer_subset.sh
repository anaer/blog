#!/usr/bin/env bash
# 生成 assets/primer-subset.css: 以模板与生成页为内容源裁剪全量 primer.css
# 用法: bash scripts/build_primer_subset.sh  (需 Node/npx, 首次运行会拉取 purgecss)
set -euo pipefail
cd "$(dirname "$0")/.."

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
cp assets/Primer@21.1.1/primer.css "$WORK/primer.css"

mkdir -p "$WORK/content"
cp templates/*.html "$WORK/content/"
if compgen -G "docs/*.html" > /dev/null; then cp docs/*.html "$WORK/content/"; fi
if compgen -G "docs/post/*.html" > /dev/null; then cp docs/post/*.html "$WORK/content/"; fi

(cd "$WORK" && mkdir -p out && npx --yes purgecss@6 --css primer.css --content content/*.html --output out > /dev/null)
cp "$WORK/out/primer.css" assets/primer-subset.css

node scripts/check_primer_subset.js

echo "OK: assets/primer-subset.css $(wc -c < assets/primer-subset.css) B (gzip $(gzip -c assets/primer-subset.css | wc -c) B)"
