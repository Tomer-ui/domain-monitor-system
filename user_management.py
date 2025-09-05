import json
from logs import logger

"""
register_user function .
reads the full file into memory.
checks for duplicate usernames.
appends new users to the list in memory(!).
opens the file in "w" mode → overwrites entire file with the updated list.
handles errors and logs them.
"""
def register_user(username, password):
    try:
        # .1. read existing users from file.
        with open('users.json', 'r') as f:
            users = json.load(f)

        # .2. check if user exists    
        if username in [user['username'] for user in users]:
            return False, "username already exists"
        
        # .3. otherwise create the new user .
        new_user = {'username': username, 'password': password}

        # .4. append new user to the list.
        users.append(new_user)

        """
        # yes. here we overwrite completely the OLD file .why u ask ?...
        # well in the future,if we develop feature to delete, or "edit" users from the file , 
        # the remains could corrupt our file .
        # so until we start to use actual DATABASES, we shell use this...
        """
        # .5. writes back the updated list back to file.
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)

        return True, "registration successful"
    
    except (IOError,json.JSONDecodeError) as e:
        logger.error(f"Error during user registration: {e}")
        return False, "server error"


""" login_user function .
pretty straight forward.
open file, load users,search loop over the list of users,
retrun true or false. & some error handling.
"""

def login_user(username, password):
    try:
        #1. open file 
        with open('users.json', 'r') as f:
            #2. load all users to a list
            users = json.load(f)
            #3. loop over each user
            for user in users:
                #4. check username and(!) password match
                if ['username'] == username and user['password'] == password :
                    return True, "login successful"
            #if no match was found,    
            return False, "invalid credentials"
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"error during user login: {e}")
        return False, "server error"


