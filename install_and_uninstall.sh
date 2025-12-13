#To install, please run these two commands in sequence. The first command requires SUDO and will will restart your computer. The second command is benign.
cd ~/ && sudo apt full-upgrade && sudo apt install git pipx gcc gcc-aarch64-linux-gnu libcap-dev python3-dev && git clone https://github.com/sp29174/GreenhousePython.git && pipx ensurepath && reboot
cd ~/ && pipx install -vvv poetry && poetry completions bash >> ~/.bash_completion && cd ./GreenhousePython && eval $(poetry env activate) && poetry install -vvv --all-groups --all-extras --compile && poetry run python ./src/main.py 
#To uninstall, please run this command:
cd ~/ && poetry env remove --all && pipx uninstall-all -vvv && rm -rf ./GreenhousePython && sudo apt purge git pipx gcc gcc-aarch64-linux-gnu libcap-dev python3-dev && sudo apt full-upgrade && reboot
