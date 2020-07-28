#!/bin/bash

function alembic_create_db() {
    echo "CREATING DATABASE"
    docker-compose run web sh -c "venv/bin/alembic revision --autogenerate -m 'Generating database'"

}

function alembic_ugrade_db() {
    echo "PREPARING UPGRADE"
    echo "PLEASE ENTER UPGRADE COMMIT MESSAGE:"
    read commit
    docker-compose run web sh -c "venv/bin/alembic revision --autogenerate -m '$commit'"
}

function alembic_nuke_db() {
    echo "DANGER: THIS WILL DELETE THE DATABASE!!!!"
    docker-compose run web sh -c "venv/bin/alembic stamp base"
}