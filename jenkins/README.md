# Jenkins CI/CD — Indistylex

**All deploys to the live server go through Jenkins on the server** — not manual `git pull`.

---

## Deploy workflow (standard)

```
git push shivam74826 develop
        │
        ▼
http://138.201.50.228:8081  →  job: indistylex-deploy  →  Build with Parameters
        │
        ▼
jenkins/deploy.sh (local)  →  git pull → pip → migrations → restart → health check
```

### Build parameters (staging / live site)

| Parameter | Value |
|-----------|--------|
| **ENVIRONMENT** | `staging` (develop branch) or `production` (main) |
| **ROLLOUT_ACTION** | `deploy` |
| **DEPLOY_TARGET** | `local` |
| **RUN_MIGRATIONS** | ✓ checked |

Job name: **`indistylex-deploy`**

### Rollout actions

| Action | What it does |
|--------|----------------|
| **deploy** | `git pull` → install deps → migrations → restart → health check → save history |
| **rollback** | Revert to previous deploy SHA from `.deploy-history` |
| **dry-run** | Print plan only — no changes |
| **restart-only** | Skip git pull, just restart service |
| **health-check** | Verify systemd + HTTP 200 |

---

## One-time server setup

Run **once** on **138.201.50.228** as root:

```bash
cd /var/www/html/indistylex
git pull shivam74826 develop
chmod +x jenkins/*.sh
sudo bash jenkins/configure-server-jenkins.sh
```

This installs Jenkins (port **8081**), plugins, GitHub SSH credential, the `indistylex-deploy` job, sudoers, and git permissions for the `jenkins` user.

First login password:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Open **http://138.201.50.228:8081**

---

## Local Jenkins (optional — tests only)

Use laptop Jenkins only to run **development** pytest — not for production deploys.

```bash
cd ~/work/indistyle/Indistylex/jenkins
./setup-local.sh
```

Open **http://localhost:8080** → `ENVIRONMENT=development` → runs tests, no server deploy.

If you must deploy from laptop Jenkins (not recommended), use `DEPLOY_TARGET=remote` and credential `indistylex-server-ssh` — see `add-ssh-credential.sh`.

---

## Files

| File | Purpose |
|------|---------|
| `../Jenkinsfile` | Pipeline: dev tests + staging/prod deploy |
| `deploy.sh` | Core deploy script (all rollout actions) |
| `configure-server-jenkins.sh` | **One-shot server Jenkins setup** |
| `environments.conf` | Branch/service/URL per environment |
| `health-check.sh` | Post-deploy HTTP + systemd check |
| `setup-server-deploy.sh` | Git remote + sudoers (called by configure script) |
| `setup-local.sh` | Laptop Jenkins for tests |
| `seed-jobs.sh` | Pre-create `indistylex-deploy` job |
| `install-server.sh` | Install Jenkins apt package only |
| `job-templates/` | Pre-built job XML |

---

## Troubleshooting

### Deploy fails: permission denied on `.git`
```bash
sudo usermod -aG www-data jenkins
sudo chgrp -R www-data /var/www/html/indistylex/.git
sudo chmod -R g+rwX /var/www/html/indistylex/.git
```

### Migrations skipped
Ensure `.env` has `DATABASE_URL=mysql://…` and `RUN_MIGRATIONS=true`. Jenkins user must be in `www-data` group (`.env` mode `640`).

### Service won't start after deploy
```bash
journalctl -u indistylex -n 50
# Rollback via Jenkins: ROLLOUT_ACTION=rollback, DEPLOY_TARGET=local
```

### Git SCM: "Repository not found"
```bash
sudo bash jenkins/configure-server-jenkins.sh   # re-seeds GitHub SSH credential
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
