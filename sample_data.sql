CREATE DATABASE OR REPLACE DATABASE sample_data;

CREATE USER 'sample_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON sample_data.* TO 'sample_user'@'localhost';

USE sample_data;
