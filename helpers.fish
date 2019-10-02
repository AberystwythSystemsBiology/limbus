function limbus-c
    docker-compose run web sh -c "find limbus -type f -name '*.pyc' -exec rm {} +"
end

function limbus-bwd
    limbus-b
    limbus-d
end

function limbus-d
    docker-compose run web sh -c "pip install -r requirements.txt && yarn install"
end

function limbus-b
    docker-compose build
end

function limbus-s
    docker-compose run --service-ports web sh -c "python limbus/run.py"
    limbus-c
end

function limbus-db-create
    limbus-db-init
    limbus-db-migrate
    limbus-db-upgrade
end

function limbus-db-init
    docker-compose run web sh -c "flask db init"
end

function limbus-db-migrate
    docker-compose run web sh -c "flask db migrate"
end

function limbus-db-upgrade
    docker-compose run web sh -c "flask db upgrade"
end