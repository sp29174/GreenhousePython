                                                     Greenhouse Automation Project
                                                                                                                                                
Welcome to the Greenhouse Automation System – a smart, Raspberry Pi-powered solution that automates plant care with automated watering (or grow lights), real-time moisture monitoring, and stunning timelapse videos. Perfect for hobbyists, educators, or IoT enthusiasts building sustainable green spaces!

🚀 Project Overview

This project integrates sensors, relays, a GUI, and camera control to create a fully autonomous greenhouse:
		
	💡Monitors soil moisture via MCP sensor.
		
	💡Automates watering (or grow lights) based on schedules and data.
		
	💡Captures hourly timelapse photos and compiles them into videos.
		
	💡Built with Python for easy customization and expansion.
		
🗝️ Key Features:
		
	💡User-friendly GUI (main.py) for control and status.
		
	💡Modular components: lighting (lights.py), moisture reading (mcp.py), watering relay (water_control.py), and camera (cameraControl.py).
		
	💡Single-relay design: Prioritize watering or lights (not both).

🛠️ Quick Start

	💡Navigate to project directory:
			cd /home/Gardener/GreenhousePython/primaryPython
			
	💡Activate virtual environment:
		source vir/bin/activate
			
	💡Run the system:
		💡python main.py

This launches the GUI, integrating all modules.

📁 File Structure:

primaryPython/
├── main.py              # Central GUI hub

├── lights.py            # Grow light scheduling

├── mcp.py               # Moisture sensor data

├── water_control.py     # Pump relay control (may need fixes)

├── cameraControl.py     # Photo capture

└── timelapse_images/    # Stored photos for video rendering

🎯 Your Contribution Tasks
	💡Help polish this into a production-ready system! Focus areas:

	💡Timelapse Automation: Schedule cameraControl.py to run hourly.

	💡Video Rendering: Compile images into MP4 videos (use OpenCV or FFmpeg).

	💡Full Integration: Ensure main.py orchestrates everything seamlessly – handle relay conflicts and error logging.

	💡Enhancements: Add config files, web dashboard, or cloud upload (bonus!).

	💡Pro Tip: Test modules individually first (python water_control.py), then integrate via main.py.

🔧 Troubleshooting & Notes
	💡Virtual Env Issues: Always activate before running code.

	💡Relay Limitation: Build watering OR lights – document your choice.

	💡Dependencies: Ensure GPIO, camera libs, and Pillow/OpenCV are installed in the venv.

	💡Hardware: Raspberry Pi with moisture sensor, relay, pump/light, and camera module.

📞 Need Help?
Contact:

	💡arosas@mcpasd.k12.wi.us
	
	💡sp29174@students.mcpasd.k12.wi.us

🤝 Contributing
Fork the repo, create a branch, and submit a PR! Start with "good first issues" like timelapse scripting. Let's grow this project together 🌱

License: MIT (feel free to adapt for your greenhouse or classroom!)
