#!/bin/bash

function limbus-pip-install() {
    echo "Enter the pip package you want to install:"
    read package
    echo ">>> Now attempting to install $package:"
    docker-compose run web sh -c "python3 -m venv venv && venv/bin/pip install $package"
    echo ">>> Writing to requirements.txt:"
    docker-compose run web sh -c "python3 -m venv venv && venv/bin/pip freeze > requirements.txt"
}

function limbus-c() {
    echo ">>>> Cleaning binary files"
    docker-compose run web sh -c "find . -type f -name '*.pyc' -exec rm {} +"
}

function limbus-create-kryton() {
    echo ">>>> Creating Kryton"
    docker-compose run web sh -c "venv/bin/python manage.py create-kryton"
}

function limbus-bwd() {
    limbus-b
    python-deps
    yarn-deps
}

function python-deps() {
    echo ">>> Setting up Python dependencies:"
    docker-compose run web sh -c "python3 -m venv venv && venv/bin/pip install -r requirements.txt"
}

function yarn-deps() {
    echo ">>> Running yarn install:"
    docker-compose run web sh -c "yarn install"
}

function limbus-b() {
    echo ">>>> Building from Dockerfile"
    docker-compose build
}

function limbus-s() {
    echo ">>>> Starting limbus daemon, to close it run limbus-d: to check logs run limbus-logs"
    docker-compose up -d
}

function limbus-logs() {
    docker-compose logs -f    
}

function limbus-d() {
    echo ">>>> Closing limbus daemon"
    docker-compose down
}

function limbus-test() {
    docker-compose run --service-ports web sh -c "venv/bin/python limbus/test_basic.py"
    limbus-c
}

function limbus-db-rebuild() {
    docker-compose run --service-ports web sh -c "venv/bin/flask db downgrade base"
    limbus-db-create
}


function limbus-db-create() {
    limbus-db-init
    limbus-db-migrate
    limbus-db-upgrade
}


function limbus-db-init() {
    docker-compose run web sh -c "venv/bin/flask db init"

}

function limbus-db-migrate() {
    docker-compose run web sh -c "venv/bin/flask db migrate"
}

function limbus-db-upgrade() {
    docker-compose run web sh -c "venv/bin/flask db upgrade"
}

function limbus-db-nuke() {
    echo ">>> Wiping database:"
    docker-compose down -v
    docker-compose run web sh -c 'rm -rf migrations && find . -path "*/migrations/*.pyc"  -delete'
    limbus-db-create
    limbus-create-kryton
}
