#the install command, a very basic outline
sudo apt full-upgrade && sudo apt install gh git pipx #&& git stuff
sudo pipx ensurepath -- global && pipx install poetry && pipx upgrade poetry && poetry completions bash >> ~/.bash_completion && eval $(poetry env activate) && poetry -vvv install --all-groups --all-extras --compile && poetry run python main.py 
