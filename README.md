To install imports, run the following command:

pip install -r requirements.txt


To generate key, run the following command:

python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
