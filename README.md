
# GALEOS
A simulator for offloading services on satellites in python language.

## Requeriments
- Docker version 28.1.1, build 4eba377 
- Prometheus-3.2.1.linux-amd64 (placed in the root folder)

## Installation
Execute the follow script to install this project:

- Initialize git:
```bash
git init
```

- Add repository:
```bash
git remote add origin [link of git repository]
```

- Fetch the Latest Changes
```bash
git pull origin containerized
```

## Usage
- Build image with docker:
```bash
docker build -t galeos .
```

- Run docker passing the following ports:
```bash
docker run -p 8000:8000 -p 9090:9090 galeos
```

- Access the port 8000 in your browser:
    - [localhost:8000/index.html](http://localhost8000/index.html)

## Authors
- [@Pedrohsgarci4](https://github.com/Pedrohsgarci4)
- [@gpcgabriel](https://www.github.com/gpcgabriel)
- [@diogo2m](https://www.github.com/diogo2m)
- [@mcluizelli](https://www.github.com/mcluizelli)

## Support
If you have any questions or suggestions, please contact us by email: pedrosachete.aluno@unipampa.edu.br, gabrieprates.aluno@unipampa.edu.br or diogomonteiro.aluno@unipampa.edu.br
