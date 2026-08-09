#!/usr/bin/env bash
# Register local ~/.ssh key in Jenkins for SSH deploy to production server.
# Usage: cd jenkins && ./setup-server-ssh-credential.sh [path-to-private-key]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JENKINS_HOME="${JENKINS_HOME:-${SCRIPT_DIR}/.jenkins_home}"
KEY_PATH="${1:-${HOME}/.ssh/id_ed25519}"
CREDENTIAL_ID="${SERVER_SSH_CREDENTIAL_ID:-indistylex-server-ssh}"
SERVER_USER="${PRODUCTION_USER:-root}"
SERVER_HOST="${PRODUCTION_HOST:-138.201.50.228}"

if [[ ! -f "${KEY_PATH}" ]]; then
  echo "ERROR: SSH private key not found at ${KEY_PATH}"
  exit 1
fi

mkdir -p "${JENKINS_HOME}"

python3 - "${JENKINS_HOME}" "${KEY_PATH}" "${CREDENTIAL_ID}" "${SERVER_USER}" "SSH deploy key for Indistylex server (${SERVER_USER}@${SERVER_HOST})" <<'PY'
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

echo ""
echo "Test SSH before Jenkins deploy:"
echo "  ssh -i ${KEY_PATH} -o BatchMode=yes ${SERVER_USER}@${SERVER_HOST} 'echo OK'"
echo ""
echo "If that fails:"
echo "  ssh-copy-id -i ${KEY_PATH}.pub ${SERVER_USER}@${SERVER_HOST}"
