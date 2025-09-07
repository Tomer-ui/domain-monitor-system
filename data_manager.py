import json
import os
from logs import logger


def get_user_domains(username: str) -> list:
    #retrieves the list of domains for a given user from the .json file.
    domain_file = f"{username}_domains.json"
    #return empty list if the file doesnt exist.
    if not os.path.exists(domain_file):
        return []
    
    try:
        with open(domain_file, 'r') as f:
            #this handle case where the file might be empty
            content = f.read()
            if not content:
                return []
            return json.loads(content)
        
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"error reading or parsing domain file for {username}: {e}")
        return []
    

def save_user_domains(username: str, domains: list):
    #saves the list of domains for a given user to their .json file
    domain_file = f"{username}_domains.json"
    try:
        with open(domain_file, 'w') as f:
            json.dump(domains, f, indent=4)
    except IOError as e:
        logger.error(f"error writing to domain file for {username}: {e}")
        
    