#!/bin/bash

function alembic_create_db() {
    echo "CREATING DATABASE"

    if [ ! -d ./services/web/migrations/versions ]; then
        mkdir -p ./services/web/migrations/versions
    fi

    docker-compose up -d

    docker-compose run web sh -c "alembic revision --autogenerate -m 'Generating database'; alembic upgrade head"
    docker-compose down

}

function alembic_upgrade_db() {
    echo "PREPARING UPGRADE"
    echo "PLEASE ENTER UPGRADE COMMIT MESSAGE:"
    read commit
    docker-compose run web sh -c "venv/bin/alembic revision --autogenerate -m '$commit'"
    docker-compose run web sh -c "venv/bin/alembic upgrade head"
    
}

function alembic_nuke_db() {
    echo "DANGER: THIS WILL DELETE THE DATABASE!!!!"
    docker-compose run web sh -c "alembic stamp base"
    docker-compose run web sh -c "rm migrations/versions/*"
    docker-compose down -v
}