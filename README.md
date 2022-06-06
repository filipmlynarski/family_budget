#### How to install:
1. install [docker-compose](https://docs.docker.com/compose/install/).
2. inside cloned repo, build the container with `docker-compose build`
3. and run the project `docker-compose up`
---
#### Run tests
simply type `./run_tests.sh`

---
#### Example requests flow to this service using curl
```bash
# create user
curl -d "username=test&password=user" localhost:8000/accounts/register/
{"username":"test","id":1}

# get user credentials
curl -d "username=test&password=user" localhost:8000/accounts/login/
{"token":"c33c9e4d486e78139dd67ad7ed0e79b21986234d"}

# create category
curl -d "name=version_2" -H 'Authorization: Token c33c9e4d486e78139dd67ad7ed0e79b21986234d' localhost:8000/budget/categories/
{"id":31,"name":"version_2","owner":4}

curl -d "name=version_2_v1" -H 'Authorization: Token c33c9e4d486e78139dd67ad7ed0e79b21986234d' localhost:8000/budget/categories/
{"id":32,"name":"version_2_v1","owner":4}

# list categories
curl -H 'Authorization: Token c33c9e4d486e78139dd67ad7ed0e79b21986234d' localhost:8000/budget/categories/
{"count":2,"next":null,"previous":null,"results":[{"id":31,"name":"version_2","owner":4,"users":[]},{"id":32,"name":"version_2_v1","owner":4,"users":[]}]}

# create new user
curl -d "username=piotrus&password=pan" localhost:8000/accounts/register/
{"username":"piotrus","id":6}

# add newly created user to created category
curl -H 'Authorization: Token c33c9e4d486e78139dd67ad7ed0e79b21986234d' localhost:8000/budget/categories/31/add_user/6
{"id":31,"name":"version_2","users":[6]}

# add expense
curl -d 'type=IN&amount=100' -H 'Authorization: Token c33c9e4d486e78139dd67ad7ed0e79b21986234d' localhost:8000/budget/budgets/31
{"user":4,"type":"IN","amount":"100.00","category":31}

# list new expense as owner of the category
curl -H 'Authorization: Token c33c9e4d486e78139dd67ad7ed0e79b21986234d' localhost:8000/budget/budgets/31
[{"user":4,"type":"IN","amount":"100.00","category":31}]

# get second user token
curl -d "username=piotrus&password=pan" localhost:8000/accounts/login/
{"token":"a29cf6a12eada92f77691c7d65adafd16ddfe0c0"}

# list expenses as guest
curl -H 'Authorization: Token a29cf6a12eada92f77691c7d65adafd16ddfe0c0' localhost:8000/budget/budgets/31
[{"user":4,"type":"IN","amount":"100.00","category":31}]

# create new user and login
curl -d "username=hacker&password=hacker" localhost:8000/accounts/register/
{"username":"hacker","id":7}
curl -d "username=hacker&password=hacker" localhost:8000/accounts/login/
{"token":"47e4efe6c4a21b77c6aed76d0ce7f28ca9f291ca"}

# try to get expenses of category that user wasn't added to
curl -H 'Authorization: Token 47e4efe6c4a21b77c6aed76d0ce7f28ca9f291ca' localhost:8000/budget/budgets/31
{"detail":"Not found."}
```
