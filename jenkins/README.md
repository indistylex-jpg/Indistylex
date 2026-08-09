# Jenkins CI/CD — Indistylex

Deploy **Indistylex** with a proper **development → staging → production** pipeline, rollback, and dry-run options.

---

## Workflow overview

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  DEVELOPMENT    │     │     STAGING      │     │    PRODUCTION     │
│  (laptop CI)    │     │  (server/live)   │     │  (server/live)    │
├─────────────────┤     ├──────────────────┤     ├───────────────────┤
│ Run pytest      │     │ deploy develop   │     │ deploy main       │
│ No server deploy│     │ branch           │     │ branch            │
└─────────────────┘     └──────────────────┘     └───────────────────┘
         │                        │                         │
         └────────────────────────┴─────────────────────────┘
                                  │
                    jenkins/deploy.sh on server
                    git pull → pip → restart → health check
```

### Rollout actions

| Action | What it does |
|--------|----------------|
| **deploy** | `git pull` → install deps → restart → health check → save history |
| **rollback** | Revert to previous deploy SHA from `.deploy-history` |
| **dry-run** | Print plan only — no changes |
| **restart-only** | Skip git pull, just restart service |
| **health-check** | Verify systemd + HTTP 200 |

---

## Quick start — local Jenkins (your laptop)

```bash
cd ~/work/indistyle/Indistylex/jenkins
./setup-local.sh
```

Open **http://localhost:8080**

### One-time: add SSH key (laptop → server)

Jenkins on your laptop SSHs to the server. Git on the server needs no credentials (configured separately).

```bash
./add-ssh-credential.sh
```

In Jenkins UI → **Credentials** → add SSH key with ID **`indistylex-server-ssh`**.

Test SSH works:
```bash
ssh root@138.201.50.228 'echo OK'
```

### Build with Parameters (common scenarios)

| Goal | ENVIRONMENT | ROLLOUT_ACTION | DEPLOY_TARGET |
|------|-------------|----------------|---------------|
| Run tests only | `development` | `deploy` | `remote` |
| Deploy develop to server | `staging` | `deploy` | `remote` |
| Deploy main to server | `production` | `deploy` | `remote` |
| Rollback staging | `staging` | `rollback` | `remote` |
| Preview deploy plan | `staging` | `dry-run` | `remote` |
| Restart app only | `staging` | `restart-only` | `remote` |

Job name: **`indistylex-deploy`** (auto-seeded by `setup-local.sh`)

---

## Server setup (one-time)

Run on **138.201.50.228** so manual deploy needs **no git credentials**:

```bash
cd /var/www/html/indistylex
git pull shivam74826 develop
chmod +x jenkins/*.sh
bash jenkins/setup-server-deploy.sh
```

After this, manual deploy is:

```bash
cd /var/www/html/indistylex
git pull shivam74826 develop
systemctl restart indistylex
```

Or with full health check + history:

```bash
ENVIRONMENT=staging ROLLOUT_ACTION=deploy bash jenkins/deploy.sh
```

### Rollback on server (no Jenkins)

```bash
cd /var/www/html/indistylex
ENVIRONMENT=staging ROLLOUT_ACTION=rollback bash jenkins/deploy.sh
```

---

## Server Jenkins (optional)

Install Jenkins on the server so deploys run locally (no SSH from laptop):

```bash
cd /var/www/html/indistylex
sudo bash jenkins/install-server.sh
```

Open **http://138.201.50.228:8081**

Build with **`DEPLOY_TARGET=local`** — runs `deploy.sh` directly on the server.

---

## Files

| File | Purpose |
|------|---------|
| `../Jenkinsfile` | Pipeline: dev tests + staging/prod deploy |
| `deploy.sh` | Core deploy script (all rollout actions) |
| `environments.conf` | Branch/service/URL per environment |
| `health-check.sh` | Post-deploy HTTP + systemd check |
| `setup-local.sh` | **One-command laptop setup** |
| `setup-server-deploy.sh` | One-time server git + sudoers setup |
| `seed-jobs.sh` | Pre-create `indistylex-deploy` job |
| `add-ssh-credential.sh` | SSH key setup instructions |
| `install-server.sh` | Install Jenkins on Ubuntu server |
| `job-templates/` | Pre-built job XML |
| `start-local.sh` / `restart-local.sh` | Run Jenkins WAR locally |
| `install-plugins.sh` | Install plugins without UI |

---

## Troubleshooting

### Old favicon/logo after deploy
Hard refresh browser: `Ctrl+Shift+R`

### Jenkins job missing "Git" SCM
```bash
./install-plugins.sh && ./restart-local.sh
```

### Deploy fails: credential `indistylex-server-ssh` not found
Run `./add-ssh-credential.sh` and add credential in Jenkins UI.

### Git SCM: "Repository not found" (private GitHub repo)
HTTPS without credentials fails. Use SSH instead:

```bash
cd jenkins
./setup-github-credential.sh ~/.ssh/id_ed25519
./restart-local.sh
```

In job **Git** section set:
- **Repository URL:** `git@github.com:shivam74826/Indistylex.git`
- **Credentials:** `indistylex-github-ssh`

Test from laptop:
```bash
ssh -T git@github.com
git ls-remote git@github.com:shivam74826/Indistylex.git HEAD
```

### `git pull` asks for password on server
Run `bash jenkins/setup-server-deploy.sh` — follow SSH deploy key instructions.

### Service won't start after deploy
```bash
journalctl -u indistylex -n 50
ENVIRONMENT=staging ROLLOUT_ACTION=rollback bash jenkins/deploy.sh
```

### Port 8080 in use
```bash
pkill -f 'jenkins.war'
./restart-local.sh
```

---

## Environment config

Edit `jenkins/environments.conf` to change branches or paths:

| Variable | Default | Meaning |
|----------|---------|---------|
| `STAGING_BRANCH` | `develop` | Branch for staging deploys |
| `PRODUCTION_BRANCH` | `main` | Branch for production deploys |
| `GIT_REMOTE` | `shivam74826` | Git remote on server |
| `STAGING_APP_DIR` | `/var/www/html/indistylex` | App path on server |

---

## Docker (optional)

Docker is **not required**. WAR mode (`./setup-local.sh`) is recommended for local use.

```bash
docker compose up -d   # if you prefer containers later
```
