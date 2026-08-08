# Jenkins CI/CD — Indistylex

Deploy **Indistylex** by triggering a Jenkins pipeline.

---

## How Jenkins works (simple)

```
You click "Build" in Jenkins
        ↓
Jenkins reads Jenkinsfile from GitHub
        ↓
Runs jenkins/deploy.sh on server
        ↓
git pull → pip install → restart indistylex
```

**You do NOT need Docker** for local Jenkins. Use the WAR method below.

---

## Local Jenkins (your ThinkPad) — step by step

### 1. Start Jenkins

```bash
cd ~/work/indistyle/Indistylex/jenkins
chmod +x *.sh
./restart-local.sh
```

Open: **http://localhost:8080**

First-time password:
```bash
cat .jenkins_home/secrets/initialAdminPassword
```

### 2. Complete setup wizard (first time only)

1. Choose **Install suggested plugins** (or skip — we install via script below)
2. Create admin user (remember username/password)
3. Save Jenkins URL as `http://localhost:8080`

### 3. Install Git plugin (required for "Pipeline from SCM → Git")

**Why Git option is missing:** the `git` plugin is not installed. Pipeline type works, but **SCM: Git** only appears after `git.jpi` is installed and Jenkins is restarted.

Run on your ThinkPad:

```bash
cd ~/work/indistyle/Indistylex/jenkins
git pull shivam74826 develop

# Fix if scripts fail with "bash\r not found"
sed -i 's/\r$//' *.sh

# Fix permissions if .jenkins_home owned by root
sudo chown -R $USER:$USER .

chmod +x *.sh
./install-plugins.sh
./restart-local.sh
```

Verify:
```bash
ls .jenkins_home/plugins/git.jpi    # must exist
```

Hard refresh browser (**Ctrl+Shift+R**), then create job again.

### 3b. WORKAROUND — use inline script (no Git plugin needed)

If Git SCM still doesn't show, use this instead — works immediately:

1. **New Item** → `indistylex-deploy` → **Pipeline** → OK
2. **Pipeline** section → Definition: **Pipeline script** (NOT "from SCM")
3. Open `jenkins/pipeline-no-git-plugin.groovy` in this repo, copy ALL text
4. Paste into the Script box → **Save**
5. Add SSH credential `indistylex-server-ssh` (see step 5 below)
6. Click **Build** to deploy

---

### 4. Create the deploy job (with Git SCM — after step 3)
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/shivam74826/Indistylex.git`
   - Branch: `*/develop`
   - Script Path: `Jenkinsfile`
6. **Save**

### 5. Add SSH credential (for deploy to server)

1. **Manage Jenkins** → **Credentials** → **System** → **Global credentials**
2. **Add Credentials**
3. Kind: **SSH Username with private key**
4. ID: `indistylex-server-ssh` (must match Jenkinsfile)
5. Username: `root`
6. Private Key: paste your server SSH private key (`~/.ssh/id_rsa` or similar)
7. Save

### 6. Trigger a deploy

1. Open job `indistylex-deploy`
2. **Build with Parameters**
3. Set:
   - **BRANCH**: `develop`
   - **GIT_REMOTE**: `origin` (or `shivam74826` if that's your remote name on server)
   - **DEPLOY_TARGET**: `production` (from local Jenkins → SSH to server)
   - **RUN_MIGRATIONS**: off
4. **Build**

Watch console output for success.

---

## Server Jenkins (production)

On server `138.201.50.228`:

```bash
cd /var/www/html/indistylex
git pull shivam74826 develop
chmod +x jenkins/*.sh
sudo bash jenkins/install-server.sh
```

Open: **http://138.201.50.228:8081**

Create same Pipeline job, but when building use:
- **DEPLOY_TARGET**: `local`
- **GIT_REMOTE**: `shivam74826`

---

## Troubleshooting

### "Pipeline" not in New Item list

Plugins not loaded. Run:
```bash
./install-plugins.sh
./restart-local.sh
```
Hard refresh browser (Ctrl+Shift+R).

### Plugin install fails in UI (timeout / stuck)

Don't use UI. Use CLI:
```bash
./install-plugins.sh
./restart-local.sh
```

### Jenkins won't start / port in use

```bash
pkill -f 'jenkins.war'
./restart-local.sh
```

### "git" plugin missing

```bash
ls .jenkins_home/plugins/git.jpi   # should exist
./install-plugins.sh && ./restart-local.sh
```

### Deploy fails: SSH credential not found

Create credential with exact ID: `indistylex-server-ssh`

### Deploy fails: permission denied on server

On server, ensure deploy script is executable:
```bash
chmod +x /var/www/html/indistylex/jenkins/deploy.sh
```

### Manual deploy (no Jenkins)

```bash
cd /var/www/html/indistylex
GIT_REMOTE=shivam74826 BRANCH=develop bash jenkins/deploy.sh
```

---

## Files

| File | Purpose |
|------|---------|
| `start-local.sh` | Start Jenkins WAR |
| `restart-local.sh` | Stop + start Jenkins |
| `install-plugins.sh` | Install plugins without UI |
| `plugins.txt` | Plugin list |
| `deploy.sh` | Actual deploy script |
| `install-server.sh` | Install Jenkins on Ubuntu server |
| `../Jenkinsfile` | Pipeline definition |

---

## Docker (optional)

Docker is **not required**. If you prefer Docker later:

```bash
sudo apt install docker.io docker-compose-v2
docker compose up -d
```

But WAR mode (`./restart-local.sh`) is simpler for local use.
