#!/usr/bin/env bash

set -euo pipefail

source venv/bin/activate

pip install --upgrade -r requirements.txt
pip freeze | sort > requirements.updated
mv requirements.updated requirements.txt

if git diff --quiet requirements.txt; then
  echo "No dependency updates detected."
  exit 0
fi

git config --global user.email "${BOT_EMAIL:-ci-bot@example.com}"
git config --global user.name "${BOT_NAME:-CI Dependency Bot}"

branch="ci/dependency-update-$(date +%Y-%m-%d)"
git checkout -b "$branch"

git add requirements.txt
git commit -m "chore: monthly dependency refresh"

git push "https://gitlab-ci-token:${CI_JOB_TOKEN}@${CI_SERVER_HOST}/${CI_PROJECT_PATH}.git" "$branch"

if [[ -n "${GITLAB_TOKEN:-}" ]]; then
  curl --request POST \
    --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    --header "Content-Type: application/json" \
    --data "{\"source_branch\":\"$branch\",\"target_branch\":\"$CI_DEFAULT_BRANCH\",\"title\":\"chore: monthly dependency refresh\"}" \
    "$CI_API_V4_URL/projects/$CI_PROJECT_ID/merge_requests"
else
  echo "Set GITLAB_TOKEN to automatically open a merge request."
fi
