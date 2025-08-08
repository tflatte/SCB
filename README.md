# SCB Fraud Detection Project

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup with Docker](#database-setup-with-docker)
- [Django Setup](#django-setup)
- [Authentication (Create Superuser)](#authentication-create-superuser)
- [Running the Server](#running-the-server)
- [Export/Import Database](#exportimport-database)
- [Running Tests](#running-tests)

---



### Prerequisites

- [Python](https://www.python.org/) (version 3.11.0)


### Installation

#### 1. Clone the repository:

Use GitHub Desktop:
   1. Click on "File" -> "Clone Repository..."
   2. Select the repository from the list or enter the repository URL.
   3. Choose a local path for cloning.
   4. Click on "Clone."

Command Line:
```sh
git clone https://github.com/tflatte/SCB.git
```

#### 2. Install Docker


- [Docker Desktop for Linux](https://docs.docker.com/desktop/install/linux-install/)
- [Docker Desktop for Mac (macOS)](https://docs.docker.com/desktop/install/mac-install/)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

after installed docker desktop, open the application and make sure it is running.

#### 3. Install dependencies
```sh
python -m venv .venv
source .venv/bin/activate
```



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

#### 5. Authentication Setup
```sh
python manage.py createsuperuser
```
Create a superuser with your credentials (e.g., username: admin, password: admin1234).
#### 5. Run the server

```
python manage.py runserver
```

### 6. Download the Model 
Since the model is too large to be stored in the repository, you need to download it from the following link:
[Download Model]()
and root directory of the project, /SCB/fraud_model.joblib

### 7. Path reference

on EDA.ipynb, and fraud_detection/services/apis/transaction.py, you need to change the path of the model and data to be the path where you downloaded the model and data.:
