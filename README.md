To create a virtual environment, run the following command:

python -m venv .venv

.venv\Scripts\activate


To install imports, run the following command ensure that you are in the venv:

pip install -r requirements.txt


To generate key, run the following command ensure that you are in the venv:

python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
