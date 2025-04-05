import configparser
import os
def create_configure():
    config = configparser.ConfigParser()

    config["General"] = {'jwt_token_expiery_hours': 2}

    with open(os.path.join("API_application", "config.ini"), "w") as configfile:
        config.write(configfile)

if __name__=="__main__":
    create_configure()