#!/usr/bin/env bash
# Print steps to add SSH credential for server deploy (one-time, local Jenkins).
set -euo pipefail

KEY_PATH="${1:-${HOME}/.ssh/id_rsa}"

cat <<EOF
==============================================
 Add SSH credential to local Jenkins
==============================================

1. Open http://localhost:8080
2. Manage Jenkins → Credentials → System → Global credentials
3. Add Credentials:
   - Kind    : SSH Username with private key
   - ID      : indistylex-server-ssh   ← must match exactly
   - Username: root
   - Private Key → Enter directly → paste key below

4. Test SSH from your laptop:
   ssh -o BatchMode=yes root@138.201.50.228 'echo OK'

If SSH fails, generate a key and add to server:
   ssh-keygen -t ed25519 -f ~/.ssh/indistylex_deploy -N ""
   ssh-copy-id -i ~/.ssh/indistylex_deploy.pub root@138.201.50.228
   # Then use ~/.ssh/indistylex_deploy as the Jenkins private key

EOF

if [[ -f "${KEY_PATH}" ]]; then
  echo "--- Public key (${KEY_PATH}.pub) — add to server if needed ---"
  cat "${KEY_PATH}.pub" 2>/dev/null || ssh-keygen -y -f "${KEY_PATH}"
else
  echo "No key at ${KEY_PATH} — generate one with ssh-keygen first."
fi
