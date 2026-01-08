#To install, please run these three commands in sequence. We provide no gaurentuee that these commands won't break your system.
sudo do-release-upgrade -d
cd ~/ && sudo apt install --install-recommends g++ libkms++-dev pkgconf ffmpeg libopenjp2-7 libcamera-dev libfmt-dev libdrm-dev git pipx gcc gcc-aarch64-linux-gnu libcap-dev python3-dev python3-tk && git clone https://github.com/sp29174/GreenhousePython.git && pipx ensurepath && reboot
cd ~/ && pipx install -vvv poetry && cd ./GreenhousePython && poetry install -vvv --all-groups --all-extras --compile && poetry run -vvv python -vvi ./src/main.py 
#To run the program, please run this command:
cd ~/ && sudo apt full-upgrade && cd ./GreenhousePython && poetry update -vvv && poetry run -vvv python -vvi ./src/main.py
#To uninstall, please run this command:
cd ~/ && poetry env remove --all && pipx uninstall-all -vvv && rm -rf ./GreenhousePython && sudo apt purge git pipx gcc gcc-aarch64-linux-gnu libcap-dev python3-dev && sudo apt full-upgrade && reboot

#NOTE that we define "the uninstaller works" to be true iff running $2, $3, $4, and $8 produces *precisely the same disk* as running sudo do-release-upgrade -d, then running sudo apt full-upgrade.
#NOTE that the uninstaller does not work.
