                                                     Terrestrial Vitrification Project
                                                                                                                                                
Welcome to the Terrestrial Vitrification Project – a smart, Raspberry Pi-powered solution that automates plant care with automated watering and grow lights, real-time moisture monitoring, and (allegedly) stunning timelapse videos. Better yet, it's open-source! Perfect for hobbyists, educators, or IoT enthusiasts building sustainable green spaces!

🚀 Project Overview

This project integrates sensors, relays, a GUI, and camera control to create a fully autonomous greenhouse:
		
	💡Monitors soil moisture via sensors.
		
	💡Automates watering and grow lights based on schedules and data.
		
	💡Captures hourly timelapse photos and compiles them into videos.
		
	💡Built with Python for easy customization.
		
🗝️ Key Features:
		
	💡User-friendly GUI (main.py) for control and status.
		
	💡Wide-open source: You can make this project better! Think of the possibilities.
		
	💡Remote design: Tired of having to touch grass to monitor the greenhouse? Now you don't have to!

🛠️ Quick Start

	😵‍💫Check: are you on the right system? 

		If you are on anything other than a Raspberry Pi running Ubuntu Server, you are on an unsupported platform. While this project may expand to cover you in the future, it doesn't right now. On the other hand, we certainly aren't going to try to stop you from ignoring this paragraph and building this anyway; just don't expect a warantee or whatever. 

	😵‍💫Check: are you a superuser?

		💡Open a terminal and type: 
			sudo echo "hello world"
		If this does not work, then you need to take this up with your administrator, because although we won't stop you from circumventing this, they certainly will.

	⏰The scary part: We haven't tested this stuff very thuroughly yet, and so 
	***IF THIS BREAKS YOUR SYSTEM, DON'T BE SURPRISED.*** 
	With that out of the way:

	💡Release upgrade: We only support Ubuntu Server 25.10 officially. Therefore, BEING VERY CLEAR THAT THIS IS PLAYING WITH FIRE, you can run this to get there:
		sudo do-release-upgrade -d
	
	💡In order to build this software, you will need some dependencies. In order to get them, you can run this command. THIS WILL RESTART YOUR COMPUTER.
		cd ~/ && sudo apt install --install-recommends g++ libkms++-dev pkgconf ffmpeg libopenjp2-7 libcamera-dev libfmt-dev libdrm-dev git pipx gcc gcc-aarch64-linux-gnu libcap-dev python3-dev python3-tk && git clone https://github.com/sp29174/GreenhousePython.git && pipx ensurepath && reboot

	💡In order to run this software, you will need other, different dependencies. In order to get them, you can run this command. It will start the script, and you should be able to control the greenhouse.
		cd ~/ && pipx install -vvv poetry && cd ./GreenhousePython && poetry install -vvv --all-groups --all-extras --compile && poetry run -vvv python -vvi ./src/main.py 
	
	💡When you want to run the script again, you can run:
		cd ~/ && sudo apt full-upgrade && cd ./GreenhousePython && poetry update -vvv && poetry run -vvv python -vvi ./src/main.py
			
	💡To uninstall the greenhouse project, we will need to make an uninstall command. We have not gotten it working yet.

📁 File Structure:

```
primaryPython/
├── .github/workflows    # Development workflows
	└── codeq.yml        # Code quality workflow
├── docs/                # Documentation that no one reads
	└── basic_usage.md   # Basic usage instructions
├── images/              # The Photographs, initially empty because you haven't taken any
	└── placeholder.jpg  # Placeholder so nothing breaks
├── src/                 # Source code folder
    ├── dataIndex.txt    # Persistent data storage file
	└── main.py          # Centralized script file
├── .gitignore           # File for git that you can ignore
├── README.md            # This exact file
├── SECURITY.md          # Infomation on security updates and reporting
├── comments.txt         # Frank J. Barth's sarcastic comments
└── pyproject.toml       # Internal dependency list
```

🔧 Troubleshooting & Notes

	💡Docs: Our glorious docs exist! Read all about the inner workings of this proghramme in the docs folder. 

📞 Need Help?
Contact:

	💡arosas@mcpasd.k12.wi.us
	
	💡sp29174@students.mcpasd.k12.wi.us

	💡frank.barth@outlook.com

🤝 Contributing
Fork the repo, create a branch, and submit a PR! Start with "good first issues" like timelapse scripting. Let's grow this project together 🌱

License: MIT
