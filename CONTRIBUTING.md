# Contributing Guidelines



## 🛠 Setting up your environment 

Setting up a LImBuS development environment couldn't be easier.

**Step Zero:** Clone the LImBuS repository using the following command.

```bash
git clone https://github.com/AberystwythSystemsBiology/LImBuS/
```

**Step One:** Set up the environment variables by creating an ```.env``` file in the root of the limbus directory and
paste the following information. You can change any of these settings, but ensure that you do this before you set up the
application.

```
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=limbus
SECRET_KEY=securitykey
WTF_CSRF_SECRET_KEY=wtfcsrfsecretkey
DOCUMENT_DIRECTORY=/limbus/documents
```


**Step Two:** Whilst the Dockerfile has been written as to ensure the best possible adherence to OCI, the easiest
way to get started is to install Docker and docker-compose. Once you have done this, in the root of the limbus directory
there exists a ```docker-helpers.sh``` file that you can use to build and run LImBuS easily. To enable this, just source it:

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
- If you can, run it through yapf before committing your code. I don't do this as much as I should.

### 🌐 HTML

- Please, for the love of god, include ```alt``` attribute for all images.
- Page titles should be presented in the following manner.

```
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
    <h2><i class="fas fa-example"></i> Title</h2>
</div>
```

- Please ensure that all page titles and ```<title>``` tags are consistent.

### 📑 CSS

- Unless things are **really** unique, please only make use of classes instead of IDs.


### Design

- Add ```Element``` should be defined as a button class of ```btn-primary```.
- Submit should be right aligned and defined as a button class of ```btn-success```.

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