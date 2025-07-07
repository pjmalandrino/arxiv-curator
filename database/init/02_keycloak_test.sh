#!/bin/bash
set -e

# Create Keycloak database and user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create Keycloak database
    CREATE DATABASE keycloak_test;
    
    -- Create Keycloak user
    CREATE USER keycloak WITH PASSWORD 'keycloak_test';
    
    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE keycloak_test TO keycloak;
    
    -- Connect to keycloak database and grant schema privileges
    \c keycloak_test
    GRANT ALL ON SCHEMA public TO keycloak;
EOSQL

echo "Keycloak test database created successfully"
