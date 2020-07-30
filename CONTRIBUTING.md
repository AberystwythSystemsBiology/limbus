# Contributing Guidelines

Note: This is deprecated.

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
