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
    docker-compose run web sh -c "find . -type f -name '*.pyc' -exec rm {} +"
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
    docker-compose build
}

function limbus-s() {
    docker-compose up -d 
}

function limbus-d() {
    docker-compose down -v
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
  docker stop limbus_postgres_1
  docker rm limbus_postgres_1
  docker-compose run web sh -c 'rm -rf migrations'
  docker-compose run web sh -c 'find . -path "*/migrations/*.pyc"  -delete'
  limbus-db-create
}
