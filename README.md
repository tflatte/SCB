# Senior Project Backend

## Table of Contents


- [Prerequisites](#prerequisites)
- [Installation](#installation)



### Prerequisites

- [Python](https://www.python.org/) (version 3.12.11)

### Installation

#### 1. Clone the repository:

Use GitHub Desktop:
   1. Click on "File" -> "Clone Repository..."
   2. Select the repository from the list or enter the repository URL.
   3. Choose a local path for cloning.
   4. Click on "Clone."

#### 2. Install Docker


- [Docker Desktop for Linux](https://docs.docker.com/desktop/install/linux-install/)
- [Docker Desktop for Mac (macOS)](https://docs.docker.com/desktop/install/mac-install/)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

after installed docker desktop, open the application and make sure it is running.

#### 3. Install dependencies (recommended anaconda)

   ```sh
   python -m pip install -r requirements.txt
   ```

#### 4. Mock postgresql
   ```sh
   docker-compose -f docker-compose.yml up -d
   ```
```sh
cd fraud_detection/
```
   ```sh
    python manage.py makemigrations
    python manage.py migrate
  ```
#### 5. Run the server

```
python manage.py runserver
```
### Export database
```
python manage.py dumpdata services --output fixtures/services.json
python manage.py dumpdata users --output fixtures/users.json
python manage.py dumpdata auth.user --output fixtures/auth.json
```
### Import database
```
python manage.py loaddata fixtures/*.json
```

### Run tests
```
python manage.py test tests 
```
### Extra information for test
```
python manage.py test tests --verbosity=3
```

superuser
admin
admin1234