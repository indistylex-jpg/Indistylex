#!/usr/bin/env bash
# Register local ~/.ssh GitHub key in Jenkins for git@github.com:shivam74826/Indistylex.git
# Usage: cd jenkins && ./setup-github-credential.sh [path-to-private-key]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JENKINS_HOME="${JENKINS_HOME:-${SCRIPT_DIR}/.jenkins_home}"
KEY_PATH="${1:-${HOME}/.ssh/id_ed25519}"
CREDENTIAL_ID="${GITHUB_SSH_CREDENTIAL_ID:-indistylex-github-ssh}"
GITHUB_REPO="${GITHUB_REPO_SSH:-git@github.com:shivam74826/Indistylex.git}"

if [[ ! -f "${KEY_PATH}" ]]; then
  echo "ERROR: SSH private key not found at ${KEY_PATH}"
  echo "Usage: ./setup-github-credential.sh ~/.ssh/id_ed25519"
  exit 1
fi

mkdir -p "${JENKINS_HOME}"

python3 - "${JENKINS_HOME}" "${KEY_PATH}" "${CREDENTIAL_ID}" "git" "GitHub SSH key for Indistylex repo" <<'PY'
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

jenkins_home, key_path, cred_id, username, description = sys.argv[1:6]
private_key = Path(key_path).read_text(encoding="utf-8").strip()
credentials_xml = Path(jenkins_home) / "credentials.xml"

def ensure_root():
    if credentials_xml.exists():
        return ET.parse(credentials_xml).getroot()
    root = ET.Element("com.cloudbees.plugins.credentials.SystemCredentialsProvider", {
        "plugin": "credentials",
    })
    domain_map = ET.SubElement(root, "domainCredentialsMap", {
        "class": "hudson.util.CopyOnWriteMap$Hash",
    })
    entry = ET.SubElement(domain_map, "entry")
    domain = ET.SubElement(entry, "com.cloudbees.plugins.credentials.domains.Domain")
    ET.SubElement(domain, "specifications")
    ET.SubElement(entry, "java.util.concurrent.CopyOnWriteArrayList")
    return root

def cred_list(root):
    entry = root.find("./domainCredentialsMap/entry")
    cred_list_el = entry.find("java.util.concurrent.CopyOnWriteArrayList")
    if cred_list_el is None:
        cred_list_el = ET.SubElement(entry, "java.util.concurrent.CopyOnWriteArrayList")
    return cred_list_el

root = ensure_root()
cl = cred_list(root)
for node in list(cl):
    id_el = node.find("id")
    if id_el is not None and id_el.text == cred_id:
        cl.remove(node)

ssh_cred = ET.SubElement(
    cl,
    "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
    {"plugin": "ssh-credentials"},
)
ET.SubElement(ssh_cred, "scope").text = "GLOBAL"
ET.SubElement(ssh_cred, "id").text = cred_id
ET.SubElement(ssh_cred, "description").text = description
ET.SubElement(ssh_cred, "username").text = username
pk_src = ET.SubElement(
    ssh_cred,
    "privateKeySource",
    {
        "class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource",
    },
)
ET.SubElement(pk_src, "privateKey").text = private_key

tree = ET.ElementTree(root)
ET.indent(tree, space="  ")
tree.write(credentials_xml, encoding="UTF-8", xml_declaration=True)
print(f"Wrote Jenkins credential '{cred_id}' → {credentials_xml}")
PY

JOB_CONFIG="${JENKINS_HOME}/jobs/indistylex-deploy/config.xml"
if [[ -f "${JOB_CONFIG}" ]]; then
  python3 - "${JOB_CONFIG}" "${GITHUB_REPO}" "${CREDENTIAL_ID}" <<'PY'
import sys
import xml.etree.ElementTree as ET

job_xml, repo_url, cred_id = sys.argv[1:4]
tree = ET.parse(job_xml)
root = tree.getroot()

for remote in root.iter("hudson.plugins.git.UserRemoteConfig"):
    url_el = remote.find("url")
    if url_el is None:
        url_el = ET.SubElement(remote, "url")
    url_el.text = repo_url

    cred_el = remote.find("credentialsId")
    if cred_el is None:
        cred_el = ET.SubElement(remote, "credentialsId")
    cred_el.text = cred_id

ET.indent(tree, space="  ")
tree.write(job_xml, encoding="UTF-8", xml_declaration=True)
print(f"Updated job SCM → {repo_url} (credential: {cred_id})")
PY
fi

echo ""
echo "GitHub SSH credential ready for Jenkins."
echo "  Credential ID : ${CREDENTIAL_ID}"
echo "  Repository    : ${GITHUB_REPO}"
echo "  Private key   : ${KEY_PATH}"
echo ""
echo "Restart Jenkins, then in the job Git section use:"
echo "  Repository URL : ${GITHUB_REPO}"
echo "  Credentials    : ${CREDENTIAL_ID}"
