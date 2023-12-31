#!/usr/bin/env bash

set -eux -o pipefail

# make sure git is installed
set +e
git --version
gitres=$?
set -e

if [[ $gitres -ne 0 ]]; then
  distronode-playbook collection-tests/install-git.yml -i ../../inventory "$@"
fi

dir="$(pwd)"

uninstall_git() {
  cd "$dir"
  distronode-playbook collection-tests/uninstall-git.yml -i ../../inventory "$@"
}

# This is kind of a hack. The uninstall playbook has no way to know the result
# of the install playbook to determine if it changed. So instead, we assume
# that if git wasn't found to begin with, it was installed by the playbook and
# and needs to be removed when we exit.
if [[ $gitres -ne 0 ]]; then
  trap uninstall_git EXIT
fi

# init sub project
mkdir "${WORK_DIR}/sub"
cd "${WORK_DIR}/sub"
touch "README.md"
git init
git config user.name 'Distronode Test'
git config user.email 'distronode-test@khulnasoft.com'
git add "README.md"
git commit -m "Initial commit."

# init super project
rm -rf "${WORK_DIR}/super" # needed when re-creating in place
mkdir "${WORK_DIR}/super"
cp -a "${TEST_DIR}/distronode_collections" "${WORK_DIR}/super"
cd "${GIT_TOP_LEVEL}"
git init

# add submodule
git -c protocol.file.allow=always submodule add "${WORK_DIR}/sub" "${SUBMODULE_DST}"

# prepare for tests
expected="${WORK_DIR}/expected.txt"
actual="${WORK_DIR}/actual.txt"
cd "${WORK_DIR}/super/distronode_collections/ns/col"
mkdir tests/.git
touch tests/.git/keep.txt  # make sure distronode-test correctly ignores version control within collection subdirectories
find . -type f ! -path '*/.git/*' ! -name .git | sed 's|^\./||' | sort >"${expected}"
set -x

# test at the collection base
distronode-test env --list-files | sort >"${actual}"
diff --unified "${expected}" "${actual}"

# test at the submodule base
(cd sub && distronode-test env --list-files | sort >"${actual}")
diff --unified "${expected}" "${actual}"
