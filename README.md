# NOREBASE CHALLENGE API

![alt text](https://github.com/kayprogrammer/norebase-challenge/blob/main/display/show.png?raw=true)

## How to run locally

* Download this repo or run: 
```bash
    $ git clone git@github.com:kayprogrammer/norebase-challenge.git
```

#### In the root directory:
- Install all dependencies
```bash
    $ pip install -r requirements.txt
```
- Create an `.env` file and copy the contents from the `.env.example` to the file and set the respective values. A postgres database can be created with PG ADMIN or psql

- Run Locally
```bash
    $ alembic upgrade heads 
```
```bash
    $ uvicorn app.main:app --reload
```

- Run With Docker
```bash
    $ docker-compose up --build -d --remove-orphans
```
OR
```bash
    $ make build
```

- Test Coverage
```bash
    $ pytest --disable-warnings -vv
```
OR
```bash
    $ make test
```

#### LIVE URL [NOREBASE Challenge Documentation](https://norebase-challenge.fly.dev)