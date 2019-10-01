<img src="limbus/app/static/images/logos/limbus_logo_250px.png" align="right" width="200px">

# LImBuS: The LIbre Biobank System

![GitHub commit activity](https://img.shields.io/github/commit-activity/w/AberystwythSystemsBiology/LImBuS)
![GitHub issues](https://img.shields.io/github/issues/AberystwythSystemsBiology/LImBuS)
![GitHub repo size](https://img.shields.io/github/repo-size/AberystwythSystemsBiology/LImBuS)

The goal of this project is to develop a Biobank Information Management System (BIMS) for the management of biospecimens and associated data that are accepted, processed, distributed, and tracked by the biorepository at Hywel Dda University Health Board's Clinical Research Centre (CRC).

# Setup

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
limbus-s
```

The first line will build LImBuS with its dependencies, and the second line will run it once that process is complete.

If you are contributing to the project, you may be interested in using the ```limbus-b``` function which will just build the project. Moreover ```limbus-d``` just gets the dependencies.


# Bug reporting and feature suggestions

Please report all bugs or feature suggestions to the [issues tracker](https://www.github.com/AberystwythSystemsBiology/limbus/issues). Please do not email me directly as I'm struggling to keep track of what needs to be fixed.

We welcome all sorts of contribution, so please be as candid as you want(!)

# License

This project is proudly licensed under the [GNU General Public License v3.0](https://raw.githubusercontent.com/AberystwythSystemsBiology/limbus/dev/LICENSE).
