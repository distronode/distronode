#!/usr/bin/env bash

set -eu -o pipefail
source virtualenv.sh
set +x
unset PYTHONPATH
export SETUPTOOLS_USE_DISTUTILS=stdlib

base_dir="$(dirname "$(dirname "$(dirname "$(dirname "${OUTPUT_DIR}")")")")"
bin_dir="$(dirname "$(command -v pip)")"

# deps are already installed, using --no-deps to avoid re-installing them
pip install "${base_dir}" --disable-pip-version-check --no-deps
# --use-feature=in-tree-build not available on all platforms

for bin in "${bin_dir}/distronode"*; do
    name="$(basename "${bin}")"

    entry_point="${name//distronode-/}"
    entry_point="${entry_point//distronode/adhoc}"

    echo "=== ${name} (${entry_point})=${bin} ==="

    if [ "${name}" == "distronode-test" ]; then
        "${bin}" --help | tee /dev/stderr | grep -Eo "^usage:\ distronode-test\ .*"
        python -m distronode "${entry_point}" --help | tee /dev/stderr | grep -Eo "^usage:\ distronode-test\ .*"
    else
        "${bin}" --version | tee /dev/stderr | grep -Eo "(^${name}\ \[core\ .*|executable location = ${bin}$)"
        python -m distronode "${entry_point}" --version | tee /dev/stderr | grep -Eo "(^${name}\ \[core\ .*|executable location = ${bin}$)"
    fi
done
