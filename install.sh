#the install command, a very basic outline
cd / && sudo apt full-upgrade && sudo apt install git pipx gcc libcap-dev python3-dev && sudo git clone https://github.com/sp29174/GreenhousePython.git && sudo pipx ensurepath && sudo reboot
cd / && pipx install poetry && pipx upgrade poetry && poetry completions bash >> ~/.bash_completion && cd ./GreenhousePython && eval $(poetry env activate) && poetry install -vvv --all-groups --all-extras --compile && poetry run python ./src/main.py 
#Why have an entire installer when you can have two very long commands.
