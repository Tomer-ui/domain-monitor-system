import json
import os
from logs import logger


DATA_DIR ='data'
os.makedirs(DATA_DIR, exist_ok=True)

"""
    Reads the user's single domain data file.
    Returns a list of domain dictionaries or an empty list if not found.
"""
def get_user_domains(username: str) -> list:
    filepath = os.path.join(DATA_DIR, f"{username}_domains.json")
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_user_domains(username: str, domains: list):
    #saves the list of domains for a given user to their .json file
    filepath = os.path.join(DATA_DIR, f"{username}_domains.json")
    with open(filepath, 'w') as f:
        json.dump(domains, f, indent=4)
    logger.info(f"domain data for '{username}' saved to {filepath}.")


        
    """  this function 
    removes a single domain from the user domain list.
    args :
    username: the user whos domain list will be modified
    domain_to_remove: the domain name to remove.

    returns:
        True if the domain was found & removed, otherwise False.
    """

def remove_user_domain(username: str, domain_to_remove: str) ->bool:
    logger.info(f"attempting to remove domain '{domain_to_remove}' for user '{username}'.")
    #1.get the current list of domains.
    current_domains = get_user_domains(username)

    #2.find total nu,ber of domains before removal.
    initial_domain_count = len(current_domains)

    #3.create a new list, withput the doamin we re,uving,
    updated_domains = [d for d in current_domains if d.get('domain') != domain_to_remove]

    #4.check if domain was actually removed,
    if len(updated_domains) < initial_domain_count:
        #5.save the new list, overwrite the old file
        save_user_domains(username, updated_domains)
        logger.info(f"successfully removed domain '{domain_to_remove}' for user '{username}'.")
        return True
    else:
        logger.warning(f"domain '{domain_to_remove}' not found for user '{username}'.")
        return False
