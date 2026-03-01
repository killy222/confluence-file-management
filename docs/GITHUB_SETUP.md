# GitHub authentication setup (Ubuntu / Linux)

Step-by-step guide to push this project to GitHub using SSH.

---

## Step 1: Add GitHub to known hosts (avoid "authenticity" prompt)

Open a terminal and run:

```bash
ssh-keyscan -t ecdsa github.com >> ~/.ssh/known_hosts
```

This adds GitHub’s host key so SSH won’t ask “Are you sure you want to continue connecting?” when you push.

---

## Step 2: Check if you already have an SSH key

```bash
ls -la ~/.ssh/id_*.pub
```

- **If you see** `id_ed25519.pub` or `id_rsa.pub`: skip to **Step 4** (show your public key and add it to GitHub).
- **If you see** “No such file or directory”: continue to **Step 3** to create a key.

---

## Step 3: Generate a new SSH key (only if you don’t have one)

Replace `your_email@example.com` with the email you use on GitHub:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""
```

- `-N ""` means no passphrase (you can use a passphrase by omitting `-N ""` and entering it when asked).

---

## Step 4: Start ssh-agent and add your key (recommended)

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

If your key is `id_rsa` instead, use:

```bash
ssh-add ~/.ssh/id_rsa
```

---

## Step 5: Copy your public key

```bash
cat ~/.ssh/id_ed25519.pub
```

(Use `id_rsa.pub` if that’s the key you created.)

Copy the **entire line** (starts with `ssh-ed25519` or `ssh-rsa`, ends with your email).

---

## Step 6: Add the key to GitHub

1. Open [https://github.com/settings/keys](https://github.com/settings/keys) and sign in.
2. Click **“New SSH key”**.
3. **Title:** e.g. `Ubuntu laptop` or `My PC`.
4. **Key type:** Authentication Key.
5. **Key:** Paste the line you copied from Step 5.
6. Click **“Add SSH key”**.

---

## Step 7: Test the connection

```bash
ssh -T git@github.com
```

You may see a warning about authenticity; type `yes` if prompted.  
You should then see something like: **“Hi username! You've successfully authenticated...”**

---

## Step 8: Push your project

From your project folder:

```bash
cd /home/www/agents

# If you haven’t committed yet
git add .
git commit -m "Initial commit"
git branch -M main

# Push to GitHub
git push -u origin main
```

If the remote already has content (e.g. a README), you may need:

```bash
git pull origin main --rebase
git push -u origin main
```

---

## Troubleshooting

| Problem | What to do |
|--------|------------|
| `Permission denied (publickey)` | Ensure the **public** key (`id_ed25519.pub`) is added in GitHub → Settings → SSH and GPG keys. Run `ssh-add -l` to confirm the key is loaded. |
| `Could not resolve hostname github.com` | Check internet; try `ping github.com`. |
| “Authenticity of host can't be established” | Run **Step 1** again, or type `yes` when SSH asks to continue. |

---

## Using HTTPS instead of SSH

If you prefer HTTPS (no SSH key):

1. Change the remote URL:
   ```bash
   git remote set-url origin https://github.com/killy222/confluence-file-management.git
   ```
2. When you `git push`, GitHub will ask for your **username** and **password**. For the password, use a **Personal Access Token** (PAT), not your GitHub password:
   - GitHub → Settings → Developer settings → Personal access tokens → Generate new token (classic).
   - Give it `repo` scope, then use the token as the password when pushing.

SSH is usually simpler once the key is set up (no token to copy on each push).
