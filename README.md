# UPISAS
Unified Python interface for self-adaptive system exemplars.

### Prerequisites 
Tested with Python 3.9.12, should work with >=3.7.

### Installation
In a terminal, navigate to the parent folder of the project and issue:
```
pip install -r requirements.txt
```

### Adding .env file
Take care to add an .env file at the following path ```UPISAS/ramses/.env``` by replacing the below empty .env file with your own values

```
ARCH= # arm64 or amd64
GITHUB_REPOSITORY_URL= #link to remote repo for config server without quotation marks {""}
GITHUB_OAUTH= #your personal access token without quotation marks ("")

```

### Run unit tests
In a terminal, navigate to the parent folder of the project and issue:
```
python -m UPISAS.tests.upisas.test_exemplar
python -m UPISAS.tests.upisas.test_strategy
python -m UPISAS.tests.swim.test_swim_interface
```
### Run
In a terminal, navigate to the parent folder of the project and issue:
```
python run.py
```

### Using experiment runner 
**Please be advised**, experiment runner does not work on native Windows. Since UPISAS also uses docker, your Windows system should have the Windows Subsystem for Linux (WSL) installed already. You can then simply use Python within the WSL for both UPISAS and Experiment Runner (restart the installation above from scratch there, and then proceed with the below).
```
cd experiment-runner
git submodule update --init --recursive
pip install -r requirements.txt
cd ..
sh run.sh 
```


