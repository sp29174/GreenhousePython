                                                     Terrestrial Vitrification Project
                                                                                                                                                
Welcome to the Terrestrial Vitrification Project – a smart, Raspberry Pi-powered solution that automates plant care with automated watering and grow lights, real-time moisture monitoring, and (allegedly) stunning timelapse videos. Better yet, it's open-source! Perfect for hobbyists, educators, or IoT enthusiasts building sustainable green spaces!

🚀 Project Overview

This project integrates sensors, relays, a GUI, and camera control to create a fully autonomous greenhouse:
		
	💡Monitors soil moisture via MCP sensor.
		
	💡Automates watering (or grow lights) based on schedules and data.
		
	💡Captures hourly timelapse photos and compiles them into videos.
		
	💡Built with Python for easy customization.
		
🗝️ Key Features:
		
	💡User-friendly GUI (main.py) for control and status.
		
	💡Wide-open source: You can make this project better! Think of the possibilities.
		
	💡Remote design: Tired of having to touch grass to monitor the greenhouse? Now you don't have to!

🛠️ Quick Start

	💡Navigate to project directory:
			cd /home/Gardener/GreenhousePython/primaryPython
			
	💡Activate virtual environment:
		source vir/bin/activate
			
	💡Run the system:
		💡python main.py

This launches the GUI, integrating all modules.

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

🎯 Your Contribution Tasks
	💡Help polish this into a production-ready system! Focus areas:

	💡Timelapse Automation: Schedule cameraControl.py to run hourly.

	💡Video Rendering: Compile images into MP4 videos (use OpenCV or FFmpeg).

	💡Full Integration: Ensure main.py orchestrates everything seamlessly – handle relay conflicts and error logging.

	💡Enhancements: Add config files, web dashboard, or cloud upload (bonus!).

🔧 Troubleshooting & Notes

	💡Dependencies: Ensure GPIO, camera libs, and Pillow/OpenCV are installed in the venv.

	💡Hardware: Raspberry Pi with moisture sensor, relay, pump, light, and camera module.

📞 Need Help?
Contact:

	💡arosas@mcpasd.k12.wi.us
	
	💡sp29174@students.mcpasd.k12.wi.us

	💡frank.barth@outlook.com

🤝 Contributing
Fork the repo, create a branch, and submit a PR! Start with "good first issues" like timelapse scripting. Let's grow this project together 🌱

License: MIT

:rage1: Ain't nobody got no time for that! My greenhouse is on fire, what do I do?
