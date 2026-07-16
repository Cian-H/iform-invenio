update auto-rollback="false":
    #!/usr/bin/env bash
    if [ ! -f update.lock ]; then
        touch update.lock
        just tag-version
        cd i-form-data-repository && docker compose -f docker-compose.full.yml --env-file ../.env down
        git pull
        cd i-form-data-repository && docker compose -f docker-compose.full.yml --env-file ../.env pull
        cd i-form-data-repository && docker compose -f docker-compose.full.yml --env-file ../.env build
        cd i-form-data-repository && docker compose -f docker-compose.full.yml --env-file ../.env up -d --wait
        rm update.lock
        if [ "{{auto-rollback}}" = "true" ]; then
            just healthcheck || just rollback
        else
            just healthcheck  || echo "Healthcheck failed. Consider rolling back by running \"just rollback\" manually if needed."
        fi
    else
        echo "Update already in progress"
    fi

merge-and-push-prod:
    #!/usr/bin/env bash
    git switch prod
    git merge main
    git switch main
    git push --all

tag-version:
    #!/usr/bin/env bash
    git tag backup-$(date +%Y%m%d-%H%M%S)
    mkdir -p versions
    cd i-form-data-repository && docker compose -f docker-compose.full.yml --env-file ../.env images | grep -v "REPOSITORY" > ../versions/$(date +%Y%m%d-%H%M%S).txt

healthcheck:
    #!/usr/bin/env bash
    for i in 1 2 3; do
        curl -f http://localhost/health && exit 0
        sleep 5
    done
    exit 1

rollback version="":
    #!/usr/bin/env bash
    current_branch=$(git branch --show-current)
    if [ -z "{{version}}" ]; then # Get last backup tag if no version specified
        version=$(git tag | grep backup | sort -r | head -n1)
    else # Or get the specified version
        version="backup-{{version}}"
    fi

    # Find corresponding version file
    version_date=${version#backup-}  # Remove 'backup-' prefix
    version_file="versions/$version_date.txt"

    if [ ! -f "$version_file" ]; then
        echo "No version file found for $version"
        exit 1
    fi

    # Read the old image versions and pull them specifically
    while read -r repo tag image_id _; do
        if [ ! -z "$repo" ]; then
            docker pull "$repo:$tag"
        fi
    done < "$version_file"

    # Then check out the version and update
    git checkout $version
    cd i-form-data-repository && docker compose -f docker-compose.full.yml --env-file ../.env down
    cd i-form-data-repository && docker compose -f docker-compose.full.yml --env-file ../.env build --no-cache
    cd i-form-data-repository && docker compose -f docker-compose.full.yml --env-file ../.env up -d
    git switch $current_branch  # Return to original branch

cleanup-versions:
    #!/usr/bin/env bash
    # Keep last 5 backup tags
    for tag in $(git tag | grep backup | sort -r | tail -n +6); do
        git tag -d $tag
        rm -f "versions/${tag#backup-}.txt"
    done

deploy *args:
    ./env.sh {{args}}
    cd i-form-data-repository && docker compose -f docker-compose.full.yml --env-file ../.env up -d --wait
    cd i-form-data-repository && docker compose -f docker-compose.full.yml --env-file ../.env exec worker bash -c "invenio db init || true; invenio db create || true; invenio alembic upgrade || true; invenio index init || true"

fmt:
    bun run prettier --write "**/*.{js,jsx,ts,tsx,html,css,scss,sass,svelte,yaml,json,markdown}"

[working-directory("../invenio-theme-iform/")]
build-theme-wheel:
    rm -rf dist
    direnv exec . uv build --package invenio-theme-iform

[working-directory("../invenio-config-iform/")]
build-config-wheel:
    rm -rf dist
    direnv exec . uv build --package invenio-config-iform

build-wheels: build-theme-wheel build-config-wheel
    echo "Building fresh wheels for local packages..."
    mkdir -p i-form-data-repository/local_wheels
    rm -f i-form-data-repository/local_wheels/*.whl
    cp ../invenio-theme-iform/dist/*.whl i-form-data-repository/local_wheels/
    cp ../invenio-config-iform/dist/*.whl i-form-data-repository/local_wheels/

test-local: build-wheels
    #!/usr/bin/env bash
    echo "Rebuilding and restarting local docker stack..."
    cd i-form-data-repository
    docker compose -f docker-compose.full.yml --env-file ../.env down
    docker build -t i-form-data-repository:latest --no-cache --build-arg INSTALL_LOCAL_WHEELS=true .
    docker compose -f docker-compose.full.yml --env-file ../.env up -d --wait
    docker compose -f docker-compose.full.yml --env-file ../.env exec worker bash -c "invenio db init || true; invenio db create || true; invenio alembic upgrade || true; invenio index init || true"
    curl -skI https://127.0.0.1:8443/ || echo "HTTPS verification failed"
# Production deployment commands using Docker/Podman

# Load AWS secrets (adjust path as needed)
load-aws-secrets:
    @if [ -f aws_secrets.sh ]; then . ./aws_secrets.sh; else echo "AWS secrets file not found"; exit 1; fi

# First-time deployment to production
prod-deploy: load-aws-secrets build-wheels
    #!/usr/bin/env bash
    echo "Deploying to production (first-time)..."
    git switch prod
    git pull origin prod
    # Build and start containers
    cd i-form-data-repository
    docker build -t i-form-data-repository:latest --no-cache --build-arg INSTALL_LOCAL_WHEELS=true .
    docker compose -f docker-compose.full.yml --env-file ../.env up -d --wait
    # Run initial database setup, migrations, and collect static assets
    docker compose -f docker-compose.full.yml --env-file ../.env exec worker bash -c " \
        invenio db init && \
        invenio db create && \
        invenio alembic upgrade head && \
        invenio collect -v && \
        invenio index init \
    "

# Update production without full redeploy (pull + migrations + static)
prod-update: load-aws-secrets build-wheels
    #!/usr/bin/env bash
    echo "Updating production deployment..."
    git switch prod
    git pull origin prod
    cd i-form-data-repository
    docker build -t i-form-data-repository:latest --no-cache --build-arg INSTALL_LOCAL_WHEELS=true .
    docker compose -f docker-compose.full.yml --env-file ../.env up -d --wait
    docker compose -f docker-compose.full.yml --env-file ../.env exec worker bash -c " \
        invenio alembic upgrade head && \
        invenio collect -v \
    "

# Clean all build artefacts and environment
prod-clean:
    @echo "Cleaning production build artefacts..."
    rm -rf .venv build dist *.egg-info
    find . -type d -name "__pycache__" -exec rm -r {} + || true
    rm -rf static node_modules
    echo "Clean complete. Re‑create environment before next deploy."
