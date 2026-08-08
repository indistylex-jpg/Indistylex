# Jenkins CI/CD — Indistylex

Deploy **Indistylex** by triggering a Jenkins pipeline instead of manual `git pull`.

| Environment | Jenkins URL | Deploy target |
|-------------|-------------|---------------|
| **Local (Docker)** | http://localhost:8080 | `production` (SSH to server) |
| **Server** | http://138.201.50.228:8081 | `local` (same machine) |

---

## 1. Local Jenkins (Docker)

```bash
cd /path/to/Indistylex/jenkins
chmod +x deploy.sh install-server.sh
docker compose up -d
```

Get initial admin password:

```bash
docker exec indistylex-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open **http://localhost:8080**, complete setup, install suggested plugins.

### Create pipeline job (local Jenkins)

1. **New Item** → name: `indistylex-deploy` → **Pipeline**
2. **Pipeline** → Definition: *Pipeline script from SCM*
3. **Git** → `https://github.com/shivam74826/Indistylex.git`, branch `develop`
4. Script Path: `Jenkinsfile`
5. Save

### SSH credential (local → production deploy)

1. **Manage Jenkins** → **Credentials** → **System** → **Global**
2. **Add Credentials** → Kind: **SSH Username with private key**
3. ID: `indistylex-server-ssh` (must match Jenkinsfile)
4. Username: `root`
5. Private key: your server SSH key

### Trigger deploy from local Jenkins

1. Open job → **Build with Parameters**
2. **BRANCH**: `develop`
3. **DEPLOY_TARGET**: `production`
4. **RUN_MIGRATIONS**: off (unless you need SQL migrations)
5. **Build**

---

## 2. Server Jenkins (production)

SSH to server and run (after pulling latest code):

```bash
cd /var/www/html/indistylex
git pull origin develop   # or shivam74826 develop
chmod +x jenkins/deploy.sh jenkins/install-server.sh
bash jenkins/install-server.sh
```

Jenkins runs on port **8081** (so it does not conflict with the app on 8000).

Open: **http://138.201.50.228:8081**

Use the printed initial admin password to finish setup.

### Create pipeline job (server Jenkins)

Same as local, but when triggering:

- **DEPLOY_TARGET**: `local`
- **GIT_REMOTE**: set to your git remote name if not `origin` (e.g. `shivam74826`)

To set default remote, add to job **Environment**:

```
GIT_REMOTE=shivam74826
```

Or configure in Jenkinsfile `environment` block.

### Firewall (if Jenkins UI not reachable)

```bash
ufw allow 8081/tcp
```

---

## 3. Manual deploy (without Jenkins)

```bash
cd /var/www/html/indistylex
GIT_REMOTE=shivam74826 BRANCH=develop bash jenkins/deploy.sh
```

---

## Pipeline parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `BRANCH` | develop | Branch to deploy |
| `RUN_MIGRATIONS` | false | Run optional MySQL migration scripts |
| `DEPLOY_TARGET` | local | `local` = this server; `production` = SSH deploy |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied on git pull | `usermod -aG www-data jenkins` and fix repo permissions |
| Service restart fails | `journalctl -u indistylex -n 50` |
| SSH deploy fails from local | Check credential ID `indistylex-server-ssh` |
| Wrong git remote | Set `GIT_REMOTE=shivam74826` in job env or when running deploy.sh |
