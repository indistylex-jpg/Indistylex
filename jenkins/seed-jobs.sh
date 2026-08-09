#!/usr/bin/env bash
# Seed Jenkins jobs from templates into local JENKINS_HOME.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JENKINS_HOME="${JENKINS_HOME:-${SCRIPT_DIR}/.jenkins_home}"
TEMPLATE_DIR="${SCRIPT_DIR}/job-templates"

mkdir -p "${JENKINS_HOME}/jobs"

for template in "${TEMPLATE_DIR}"/*.xml; do
  [[ -f "${template}" ]] || continue
  job_name="$(basename "${template}" .xml)"
  job_dir="${JENKINS_HOME}/jobs/${job_name}"
  mkdir -p "${job_dir}/builds"
  echo "0" > "${job_dir}/nextBuildNumber"
  printf 'lastBuild\nlastStableBuild\nlastSuccessfulBuild\nlastFailedBuild\nlastUnstableBuild\nlastUnsuccessfulBuild\n' > "${job_dir}/builds/permalinks"
  cp "${template}" "${job_dir}/config.xml"
  echo "  ✓ Seeded job: ${job_name}"
done

echo "Jobs seeded in ${JENKINS_HOME}/jobs/"
