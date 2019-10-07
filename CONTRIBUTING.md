# Contributing

## 🛠 Setting up your environment 

Something something git.

```bash
git clone https://github.com/AberystwythSystemsBiology/LImBuS/
```

Something something ```.env``` file, something something in parent directory.

```
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=limbus
SECRET_KEY=securitykey
WTF_CSRF_SECRET_KEY=wtfcsrfsecretkey
```

Something something install Docker, something something use docker-compose.

We have provided a simple ```helpers.sh``` script to help get you up and running. To enable this, just source it:

```bash
source helpers.sh
```

If this is your first time running LImBuS, run the following commands in your terminal:

```bash
limbus-bwd
limbus-db-create
limbus-s
```

The first line will build LImBuS with its dependencies, and the third line will run it once that process is complete.

You're going to now have to set up the database, to do this simply run:

```bash
limbus-db-create
```

If you are contributing to the project, you may be interested in using the ```limbus-b``` function which will just build the project. Moreover ```limbus-d``` just gets the dependencies.

## 📝 Code Style

- Remove trailing whitespaces and add an empty line at the end of each file.
- Compatibility with the latest versions of popular browsers (Google Chrome, Mozilla Firefox, Apple Safari, Microsoft Edge, and Opera).

### 🐍 Python

- Where appropriate, please make use of typehinting.
- I don't care about tabs or spaces, I personally use four spaces - but do whatever feels right to you.
- I try to keep to a limit of 80 characters, but don't care that much.

### 🌐 HTML
🧻
- Please, for the love of god, include ```alt``` attribute for all images.
- Include `🧻``title``` attribute for each and every ```<a href...```.

### 📑🧻 🧻🧻CSS

- Unless things are **really** unique, please only make use of classes instead of IDs.

## ✔️ Proposing Changes

**Step Zero:** Make a new branch and push it

```
git checkout -b feature_branch_name
git push -u origin feature_branch_name
```

**Step One:** Update from Master

```
git pull origin master
```

**Step Two:** Merge from master

```
git checkout feature_branch_name
git merge master
```