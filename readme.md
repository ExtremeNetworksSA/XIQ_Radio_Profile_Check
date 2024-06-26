# XIQ Radio Profile Check
### XIQ_Radio_Profile_Check
## Purpose
This script will check settings of a radio profile. The script will inform you what the max power is set to, if Band Steering is enabled and what mode is being used, and if weak signal probe suppression is enabled.

## Information
### Authentication
The script will prompt for you XIQ credentials. 
>You can also manually enter an API token on line 12. Token needs the 'radio-porfile:r' permission
### Collecting Radio Profile Information
The script will prompt user to select a radio profile. The script will present the radio profiles 10 at a time in alphabetical order. The user can select the radio profile they would like to check by enter the associated number in the prompt.
```
Please select the Radio profile you would like to check.
The script will list out 10 Radio Profiles at a time
There are a total of 29 Radio Profiles.
        1.      410c_Sensor_5
        2.      5010_24
        3.      5010_5
        4.      5010_6
        5.      AP150W-11ac-Profile
        6.      AP150W-11ng-Profile
        7.      AP150W-Copy
        8.      Copy of Sheng_5Ghz
        9.      Gones_150W
        10.     Sheng-6Hz
        n.      List next batch of Radio Profiles
Please enter 1 - 10 , n (for next page):
```

## Running the script
open the terminal to the location of the script and run this command
```
python XIQ_Radio_Profile_Check.py
```

## Requirements
There are additional modules that need to be installed in order for this script to function. They are listed in the requirements.txt file and can be installed with the command 'pip install -r requirements.txt' if using pip.

