# staibot
A simple Discord bot to allow users to auto-assign themselves roles. Useful for role-based access control to certain areas of a server.
Written for Staiain's rhythm game community server (https://twitch.tv/staiain), but would work elsewhere.

Note that this is a relatively early version of the bot, and regular updates will occur.

### Current features
- Allows users to self-assign roles in a server. This is useful if users want to enrol themselves into certain groups, etc.
- Allows users to enable a "notification role", which allows them to be mentioned if an administrator sees fit (`!notify`).
- Uses a MongoDB database for persistence.

### Planned features
- Add a rule system for specified roles, so a user would have to read and acknowledge a set of rules before the bot assigns them their role.
- Create a configuration file, so that the bot can be more easily tailored to specific setups and requirements
- Implement a plugin system for developers to extend the bot's functionality
- If the bot ends up storing data about users, then implement a ToS message for the server admin to accept

### Requirements
- Python 3.6 or later (can be obtained on Ubuntu >= 16.10 by installing the `python3.6` package.)  
If you choose to use a different distribution, make sure you can get python3.6 working, as well as pip.
- A working instance of MongoDB.
- discord.py, asyncio and pymongo libraries (`pip3 install discord.py asyncio pymongo` should do the trick)
- A Discord app - you'll need the client token to allow the bot to talk to Discord's API. You can create one here: https://discordapp.com/developers/applications/me
- The bot should have a role that allows it to read and send messages, and manage roles. Additional roles are not needed and may present  a security risk.

### Installation on Ubuntu >= 16.10
1. Follow this tutorial on installing MongoDB on Ubuntu: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/ - except when adding the repository, replace "xenial" with "yakkety" for 16.10, or "zesty" for 17.04. For example, the command would look like this for a 17.04-based system:  
`echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu zesty/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list`
2. Run `sudo apt update` to refresh the package manager lists.
3. Install these packages:  
`sudo apt install python3.6 python3-pip mongodb-org`  
4. Install the dependencies from pip as outlined in the requirements section of this readme.
5. At the bottom of bot.py, add the following line, where <YOUR CLIENT TOKEN> is the token you obtained earlier from Discord:  
`client.run("<YOUR CLIENT TOKEN>")`
6. Run the bot using `python3.6 bot.py`.

### Known issues:
None. No code is perfect, so if you find any, feel free to open an issue.
