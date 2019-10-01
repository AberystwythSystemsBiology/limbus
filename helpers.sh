#!/bin/bash

function limbus-c() {
    docker-compose run web sh -c "find limbus -type f -name '*.pyc' -exec rm {} +"
}

function limbus-bwd() {
    limbus-b
    limbus-d
}

function limbus-d() {
    docker-compose run web sh -c "pip install -r requirements.txt && yarn install"
}

function limbus-b() {
    docker-compose build

}

function limbus-s() {
    docker-compose run --service-ports web sh -c "python limbus/run.py"
    limbus-c
}

function limbus-db-create() {
    limbus-db-init
    limbus-db-migrate
    limbus-db-upgrade
}

function limbus-db-init() {
    docker-compose run web sh -c "flask db init"

}

function limbus-db-migrate() {
    docker-compose run web sh -c "flask db migrate"
}

function limbus-db-upgrade() {
    docker-compose run web sh -c "flask db upgrade"
}