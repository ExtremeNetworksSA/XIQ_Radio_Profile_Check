# XIQ Radio Profile Check
### XIQ_Radio_Profile_Check
## Purpose
This script will check settings of a radio profile. The script will inform you what the max power is set to, if Band Steering is enabled and what mode is being used, and if weak signal probe suppression is enabled.

## Information
### Authentication
The script will prompt for you XIQ credentials. 
>You can also manually enter an API token on line 12. Token needs the 'radio-porfile:r' permission
### Collecting Radio Profile Information
The script will prompt user for the name of the Radio Profile they would like to check

## Running the script
open the terminal to the location of the script and run this command
```
python XIQ_Radio_Profile_Check.py
```

## Requirements
There are additional modules that need to be installed in order for this script to function. They are listed in the requirements.txt file and can be installed with the command 'pip install -r requirements.txt' if using pip.

