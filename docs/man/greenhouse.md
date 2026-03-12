# NAME
greenhouse - A Python-based management interface for greenhouse automation.

# SYNOPSIS
**python3 main.py** [OPTIONS]

# DESCRIPTION
**GreenhousePython** is a graphical and command-line utility designed to control greenhouse hardware. It provides interfaces for camera monitoring, irrigation (water control) for multiple garden beds, and light intensity scaling.

The application uses the GTK4 toolkit for its graphical interface and Typer for command-line interactions.

# CONFIGURATION
The application requires a configuration file named **cfg.txt** located in the working directory.

### Required fields in cfg.txt:
* **beds**: The number of garden beds to initialize for water control.
* **file_name_prefix**: The prefix used for saving and retrieving camera images.

# INTERFACE SECTIONS
The interface is divided into the following notebook pages:

* **Camera Control**: Displays placeholders or active streams from the greenhouse camera.
* **Water Control**: Provides individual control tabs for each "Bed" defined in the configuration.
* **Light Control**: Features a slider to adjust light intensity from 0 to 1.
* **Misc**: Additional system controls and settings.

# EXIT STATUS
* **0**: Success.
* **1**: Failure (e.g., missing cfg.txt or dependency errors).

# SEE ALSO
The project source and issues can be found at: 
https://github.com/sp29174/GreenhousePython