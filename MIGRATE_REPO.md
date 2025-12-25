# Moving Lectra to a New Repository

## Option 1: Keep Git History (Recommended)

If you want to keep all your git history, follow these steps:

### Step 1: Commit your current changes
```bash
git commit -m "Transform project to Lectra - AI-Powered Lecture Note Taker"
```

### Step 2: Remove the old remote
```bash
git remote remove origin
```

### Step 3: Add your new repository as the remote
```bash
# Replace with your new repository URL
git remote add origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git
```

### Step 4: Push to the new repository
```bash
git push -u origin main
```

---

## Option 2: Fresh Start (No History)

If you want to start fresh without the old repository's history:

### Step 1: Remove the old git history
```bash
rm -rf .git
```

### Step 2: Initialize a new git repository
```bash
git init
git add -A
git commit -m "Initial commit: Lectra - AI-Powered Lecture Note Taker"
```

### Step 3: Add your new repository as the remote
```bash
# Replace with your new repository URL
git remote add origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git
```

### Step 4: Push to the new repository
```bash
git branch -M main
git push -u origin main
```

---

## Before You Start

1. **Create your new repository** on GitHub (or your git hosting service) first
2. **Don't initialize it** with a README, .gitignore, or license (since you already have these)
3. **Copy the repository URL** (HTTPS or SSH)

## Notes

- If you use **Option 1**, all commit history from the original repository will be preserved
- If you use **Option 2**, you'll have a clean slate with just one initial commit
- Make sure to update any references to the old repository in your code/docs if needed

