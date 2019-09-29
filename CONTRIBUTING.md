# Contributing

## Code Style

- Remove trailing whitespaces and add an empty line at the end of each file.
- Compatibility with the latest versions of popular browsers (Google Chrome, Mozilla Firefox, Apple Safari, Microsoft Edge, and Opera).

### Python

- Where appropriate, please make use of typehinting.
- Tabos or spaces, I don't care.

### HTML

- Please, for the love of god, include ```alt``` attribute for all images.
- Include ```title``` attribute for each and every ```<a href...```.

### CSS

- Unless things are **really** unique, please only make use of classes instead of IDs.

## Proposing Changes

### Make a new branch and push it

```
git checkout -b feature_branch_name
git push -u origin feature_branch_name
```

### Update from Master

```
git pull origin master
```

### Merge from master

```
git checkout feature_branch_name
git merge master
```