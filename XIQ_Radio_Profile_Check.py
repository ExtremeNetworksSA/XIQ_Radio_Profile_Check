#!/usr/bin/env python3
import requests
import json
import sys
import logging
import os
import getpass
from pprint import pprint as pp
from requests.exceptions import HTTPError


# token can be added to bypass credential login. The token would need to have 'radio-porfile:r' permission
XIQ_token = ''


PATH = os.path.dirname(os.path.abspath(__file__))

# console output 
class CustomFormatter(logging.Formatter):
	# Git Shell Coloring - https://gist.github.com/vratiu/9780109
	GREY = "\x1b[38;20m"
	RED   = "\033[1;31m"  
	BLUE  = "\033[1;34m"
	GREEN = "\033[0;32m"
	YELLOW = "\033[0;33m"
	BOLD_RED = "\x1b[31;1m"
	RESET = "\033[0;0m"
	format = '%(levelname)s: %(message)s'
	
	FORMATS = {
	        logging.DEBUG: GREEN + format + RESET,
	        logging.INFO: BLUE + format + RESET,
	        logging.WARNING: YELLOW + format + RESET,
	        logging.ERROR: RED + format + RESET,
	        logging.CRITICAL: BOLD_RED + format + RESET
	    }
	
	def format(self, record):
		log_fmt = self.FORMATS.get(record.levelno)
		formatter = logging.Formatter(log_fmt)
		return formatter.format(record)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG) # this is needed to get all levels, and therefore filter on each handler

# create console handler for logger.
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(level=logging.INFO)
consoleHandler.setFormatter(CustomFormatter())
logger.addHandler(consoleHandler)


# XIQ info
URL = "https://api.extremecloudiq.com"
headers = {"Accept": "application/json", "Content-Type": "application/json"}

def getAccessToken(XIQ_username, XIQ_password):
    url = URL + "/login"
    payload = json.dumps({"username": XIQ_username, "password": XIQ_password})
    response = requests.post(url, headers=headers, data=payload)
    if response is None:
        log_msg = "ERROR: Not able to login into ExtremeCloudIQ - no response!"
        raise TypeError(log_msg)
    if response.status_code != 200:
        log_msg = f"Error getting access token - HTTP Status Code: {str(response.status_code)}"
        raise TypeError(log_msg)
    data = response.json()

    if "access_token" in data:
        #print("Logged in and Got access token: " + data["access_token"])
        headers["Authorization"] = "Bearer " + data["access_token"]
        return 0

    else:
        log_msg = "Unknown Error: Unable to gain access token"
        raise TypeError(log_msg)

def __get_api_call(url):
        try:
            response = requests.get(url, headers= headers)
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err} - on API {url}')
            raise ValueError(f'HTTP error occurred: {http_err}') 
        if response is None:
            log_msg = "ERROR: No response received from XIQ!"
            raise ValueError(log_msg)
        if response.status_code != 200:
            log_msg = f"Error - HTTP Status Code: {str(response.status_code)}"
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.warning(f"\t\t{response.text}")
            else:
                if 'error_message' in data:
                    logger.warning(f"\t\t{data['error_message']}")
                    raise ValueError(log_msg)
            raise ValueError(log_msg) 
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ValueError(f"Unable to parse json data - {url} - HTTP Status Code: {str(response.status_code)}")
        return data


def collectRadioProfiles(pageSize):
    page = 1
    pageCount = 1

    radioProfiles = []
    while page <= pageCount:
        url = URL + "/radio-profiles?page=" + str(page) + '&limit=' + str(pageSize)
        try:
            rawList = __get_api_call(url)
        except ValueError as e:
            logger.error(f"API to collect Radio Profiles failed with {e}")
            print('script is exiting...')
            raise SystemExit
        except Exception as e:
            logger.error(f"API to collect Radio Prfiles failed with {e}")
            print('script is exiting...')
            raise SystemExit 
        radioProfiles = radioProfiles + [profile for profile in rawList['data']]

        pageCount = rawList['total_pages']
        print(f"completed page {page} of {rawList['total_pages']} collecting Radio Profiles")
        page = rawList['page'] + 1 

    return radioProfiles

def checkRadioUsageOpt(radio_usage_opt_id):
    url = URL + '/radio-profiles/radio-usage-opt/' + str(radio_usage_opt_id)
    try:
        rawData = __get_api_call(url)
    except ValueError as e:
        logger.error(f"API to collect Radio Profiles failed with {e}")
        print('script is exiting...')
        raise SystemExit
    except Exception as e:
        logger.error(f"API to collect Radio Prfiles failed with {e}")
        print('script is exiting...')
        raise SystemExit 
    logging.info(f"Band Steering is set to {rawData['enable_band_steering']}")
    logging.info(f"Band Steering Mode is set to {rawData['band_steering_mode']}")
    logging.info(f"Weak Signal Probe Suppression Request is set to {rawData['enable_weak_signal_probe_request_suppression']}")
    if rawData['enable_weak_signal_probe_request_suppression']:
        logging.info(f"The Weak SNR is set to {rawData['weak_snr_threshold']}")
    logging.info(f"High Density is set to {rawData['enable_high_density']}")
    if rawData['enable_high_density']:
        logging.info(f"High Density Data Rates supported Data Rates is set to {rawData['management_frame_basic_data_rate']}")
        logging.info(f"High Density - Suppress successive requests probe request is set to {rawData['enable_suppress_successive_probe_request']}")
        if rawData['probe_response_reduction_option']:
            logging.info(f"high Density - probe response reduction option is set to {rawData['probe_response_reduction_option']}")
        else:
            logging.info("high Density - No probe response reduction option selected")


def main():
    if XIQ_token:
        headers["Authorization"] = "Bearer " + XIQ_token
    else:
        print("Enter your XIQ login credentials")
        username = input("Email: ")
        password = getpass.getpass("Password: ") 
        try:
            login = getAccessToken(username, password)
        except TypeError as e:
            print(e)
            raise SystemExit
        except:
            log_msg = "Unknown Error: Failed to generate token"
            print(log_msg)
            raise SystemExit
    
    logging.info("You can quit the app at any time by entering 'q' or 'quit' \n")

    valid_radio_profile = False


    existingProfiles = collectRadioProfiles(pageSize=100)
    existingProfilenameMap = {profile['name']: profile for profile in existingProfiles}
    existingProfileList = list(existingProfilenameMap.keys())
    existingProfileList.sort()

    while not valid_radio_profile:
        sizeofbatch = 10
        batchcount = 0
        print("\nPlease select the Radio profile you would like to check.")
        if sizeofbatch < len(existingProfileList):
            print(f"The script will list out {sizeofbatch} Radio Profiles at a time")
            print(f"There are a total of {len(existingProfileList)} Radio Profiles.")
        for i in range(0, len(existingProfileList), sizeofbatch):
            batch = existingProfileList[i:i+sizeofbatch]
            # User enters name of radio profile 
            count = 1
            countMap = {}
            for radioProfileName in batch:
                countMap[count] = radioProfileName
                print(f"\t{count}.\t{radioProfileName}")
                count +=1
            input_msg = f"Please enter 1 - {count-1} "
            if i+sizeofbatch < len(existingProfileList):
                print(f"\tn.\tList next batch of Radio Profiles")
                input_msg += ", n (for next page): "
            else:
                input_msg += ": "
            radioProfileSelection = input(input_msg)
            if radioProfileSelection.lower() == 'q' or radioProfileSelection.lower() == 'quit':
                logging.error("script is exiting....\n")
                raise SystemExit
            elif radioProfileSelection.lower() == 'n' or radioProfileSelection.lower() == 'next':
                batchcount = batchcount + sizeofbatch
                continue
            else:
                try:
                    radioProfileSelection = int(radioProfileSelection)
                except:
                    logging.warning("Please enter a valid response!!\n")
                    continue
            if 0 < radioProfileSelection < count:
                valid_radio_profile = True
                checkProfile = existingProfilenameMap[countMap[radioProfileSelection]]
                #print(checkProfile)
            else:
                logging.warning("Please enter a valid response!!\n")
                continue
            break


    # get the name of the profile
    logger.info(f"The Profile name is {checkProfile['name']}")
    # get the max transmit power
    logger.info(f"Max Power is set to {checkProfile['max_transmit_power']}")

    # Check if Band Steering is enabled and get the band steering mode
    # Get the Weak Signal Probe Suppression Request
    checkRadioUsageOpt(checkProfile['radio_usage_optimization_id'])






if __name__ == '__main__':
	main()