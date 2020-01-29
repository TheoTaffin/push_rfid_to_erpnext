import os
import time
import requests
import json
import urllib3
import datetime
import local_config as config

# WIthout certificat :
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# bash script to fetch RFID tag :
getTagCmd = "sudo nfc-list | sed -n '6p' | awk '{print $3" + '":"' + "$4" + '":"' + "$5" + '":"' + "$6}'"

# Setting up headers for requests
headers = {
    'Authorization': "token " + config.ERPNEXT_API_KEY + ":" + config.ERPNEXT_API_SECRET,
    'Accept': 'application/json'
}

# Program doesn't stop :
while True:
    try:

        os.system(getTagCmd)
        # get the rfid tag and supress blank space at the end
        rfid_tag = os.popen(getTagCmd).read().strip()

        if (rfid_tag != ''):

            url = config.ERPNEXT_URL + "/api/resource/RFID?fields=[%22customer_name%22]" \
                                       "&filters=[[%22RFID%22,%22rfid_tag%22,%22=%22,%22" + rfid_tag + "%22]]"

            r = requests.get(url, headers=headers)
            d = r.json()['data']

            # check if RFID exists in DB
            if (d.__len__() != 0):

                # check if a customer is attributed to the badge
                if (d[0]['customer_name'] != None):
                    print("Acces autorise")

                    url = config.ERPNEXT_URL + "/api/resource/Badge Checkin"
                    timestamp = datetime.datetime.now().__str__()
                    customer_name = d[0]['customer_name']

                    data = {
                        "date_heure": timestamp,
                        "rfid_tag": rfid_tag,
                        "customer_name": customer_name
                    }

                    # convert 'dict to 'str'
                    data = {"data": json.dumps(data)}

                    # push data to ERPNEXT
                    r = requests.post(url, data=data, headers=headers)
                    time.sleep(config.POST_DETECTION_DELAY)

                else:
                    print("Acces refuse")
            else:
                print("Acces refuse")

        else:
            print("Pas de carte detectee")

    finally:
        time.sleep(config.CHECK_BADGE_FREQUENCY)