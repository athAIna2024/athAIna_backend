To create a virtual environment, run the following command:

python -m venv .venv

.venv\Scripts\activate


To install imports, run the following command ensure that you are in the venv:

pip install -r requirements.txt

pip freeze > requirements.txt (for Docker)


To generate key, run the following command ensure that you are in the venv:

python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'


To uninstall a package along with its dependencies
1. First install pip, autoremove
    - pip install pip-autoremove
   
pip-autoremove google-generativeai -y

To install Docker Desktop on Windows,

1. Go to the Windows terminal and run the following command:
    - wsl --install
    - provide a username and password for the Linux subsystem
    - then hush login to the Linux subsystem by running the following command:
    - touch ~/.hushlogin
    - sudo apt-get update
    - sudo-apt get install mysql-server
    - sudo service mysql start
2. Install Docker Desktop from the official website.
 