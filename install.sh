#the install command, a very basic outline
cd / && sudo apt full-upgrade && sudo apt install git pipx && sudo git clone https://github.com/sp29174/GreenhousePython.git && sudo pipx ensurepath --global && pipx install poetry && pipx upgrade poetry && poetry completions bash >> ~/.bash_completion && cd ./GreenhousePython && eval $(poetry env activate) && poetry -vvv install --all-groups --all-extras --compile && poetry run python main.py 
#Why have an entire installer when you can have a single very long command.
