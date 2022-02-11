# Contributing Guidelines

## ✔️ Proposing Changes

All new contributions are required to follow a standard naming convention for branches:

- `feature/name-of-the-feature`
- `fix/name-of-the-fix`


If you're not part of the project, feel free to fork the project and create a new branch in your new fork. If you've been assigned read/write access to the project you can use the project repository to create a branch.

Once you have done that, go to the project directory and run:

```
git pull
git checkout -b feature/name-of-the-feature
```

Once you've made your changes make your push:

```
git push -u origin feature/name-of-the-feature
```

After you finish working, commit and push your code to your branch and create a pull request to merge the branch into `dev` branch.

Assign someone for code review. The idea is to learn from each other, to make sure that all coding standards are met, and that code style is respected. Wait for the review, and if there are any questions/suggestions/fixes/changes requested from the person - the reviewer will request it with clear comments. The process will then start again until all comments are resolved and the reviewer accepts the pull request.

Once your code has been successfully reviewed, your branch will be merged into the `dev` branch.


## 📝 Code Style

- Remove trailing whitespaces and add an empty line at the end of each file.
- Compatibility with the latest versions of popular browsers (Google Chrome, Mozilla Firefox, Apple Safari, Microsoft Edge, and Opera).

### 🐍 Python

- Where appropriate, please make use of typehinting.
- I don't care about tabs or spaces, I personally use four spaces - but do whatever feels right to you.
- I try to keep to a limit of 80 characters, but I don't care that much.
- `black` is run by our CI system so that should cover most of our bases. 


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


