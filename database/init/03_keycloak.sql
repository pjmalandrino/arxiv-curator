-- Create keycloak user and database
CREATE USER keycloak WITH ENCRYPTED PASSWORD 'keycloak_password';
CREATE DATABASE keycloak OWNER keycloak;
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;
