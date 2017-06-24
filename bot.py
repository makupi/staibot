import discord
import asyncio
import pymongo

client = discord.Client()

dbconn = pymongo.MongoClient()
database = dbconn.staibot
roles = database.roles

@client.event
async def on_ready():
	print("Bot is ready.")
	print("Signed in as {} ({})".format(client.user.name, client.user.id))
	print("=" * 80)
	print("Joined to servers:")
	
	for s in client.servers:
		print("{} ({})".format(s.name, s.id))
		print("with roles:")
		for role in s.roles:
			print("    {} ({})".format(role.name, role.id))

@client.event
async def on_message(message):
	# Command for help.
	if message.content.lower().startswith("!staibot help"):
		msg =  "```User commands:\n"
		msg += "!notify <enable/disable>           assigns the notification role for this server.\n"
		msg += "!role <add/remove> <rolename>      assigns any secondary roles for this server.\n"
		msg += "!role list                         lists all roles on the server.\n"
		msg += "!staibot help                      displays this help text.\n"

		if message.author.server_permissions.administrator:
			msg += "\nAdministrator commands:\n"
			msg += "!admin serverinfo                  lists all relevant server info, e.g. role ids, server id etc.\n"
			msg += "!admin addrole <rolename> <roleid> adds a role to the server. use !admin serverinfo to get role ID.\n"
			msg += "!admin removerole <rolename>       removes a role from the server.\n"
			msg += "!admin notifyrole <roleid>         sets the notification role for this server, used by the !notify command\n"

		msg += "```"
		await client.send_message(message.author, msg)

	# Command to enable notifications.
	if message.content.lower().startswith("!notify enable"):
		print("Enabling notifications for {} ({}).".format(message.author.name, message.author.id))
		
		# Get the role so that it can be assigned.
		role_db = roles.find_one({"sid": message.server.id, "rolename": "$notify"})
		role_object = None
		
		if role_db is not None:
			for role in message.server.roles:
				if role_db["roleid"] == role.id:
					role_object = discord.utils.get(message.server.roles, id=role.id)
			
			if role_object is not None:
				await client.add_roles(message.author, role_object)
				await client.send_message(message.channel, "{} - notifications enabled :ok_hand:".format(message.author.mention))
			
			else:
				await client.send_message(message.channel, "The notification role no longer exists. Use admin commands to fix.")
		
		else:
			await client.send_message(message.channel, "I have no idea what role to assign. Use admin commands to fix.")

	# Command to disable notifications.
	if message.content.lower().startswith("!notify disable"):
		print("Disabling notifications for {} ({}).".format(message.author.name, message.author.id))
		
		# Get the role so that it can be assigned.
		role_db = roles.find_one({"sid": message.server.id})
		role_object = None
		
		if role_db is not None:
			for role in message.server.roles:
				if role_db["roleid"] == role.id:
					role_object = discord.utils.get(message.server.roles, id=role.id)
			
			if role_object is not None:
				await client.remove_roles(message.author, role_object)
				await client.send_message(message.channel, "{} - notifications disabled :ok_hand:".format(message.author.mention))
			
			else:
				await client.send_message(message.channel, "The notification role no longer exists. Use admin commands to fix.")
		
		else:
			await client.send_message(message.channel, "I have no idea what role to remove. Use admin commands to fix.")

	# Command to list roles for users.
	if message.content.lower().startswith("!role list"):
		msg = "Roles for server \"{}\":\n```".format(message.server.name)
		
		notifs = False
		docs = roles.find({"sid": message.server.id})
		if docs.count() > 0:
			for document in docs:
				if document["rolename"] != "$notify":
					msg += " {}\n".format(document["rolename"])
				else:
					notifs = True
		else:
			msg += " There are no roles.\n"
		
		if notifs:
			msg += " Notifications are enabled for this server.\n"

		msg += "```"
		await client.send_message(message.channel, msg)

	# Command to add a role for a user.
	if message.content.lower().startswith("!role add"):
		
		if len(message.content.split(" ")) == 3:
			role_name = message.content.split(" ")[2]
			
			if roles.find_one({"sid": message.server.id, "rolename": role_name}) is not None:
				role_id = roles.find_one({"sid": message.server.id, "rolename": role_name})["roleid"]
				role_object = discord.utils.get(message.server.roles, id=role_id)

				if role_object is not None:
					await client.add_roles(message.author, role_object)
					await client.send_message(message.channel, "{} - role \"{}\" added :ok_hand:".format(message.author.mention, role_name))

				else:
					await client.send_message("That role no longer exists on the server.")

			else:
				await client.send_message(message.channel, "That role doesn't exist.")

		else:
			await client.send_message(message.channel, "Invalid command syntax. See `!staibot help` for usage.")

	# Command to remove a role for a user.
	if message.content.lower().startswith("!role remove"):
		
		if len(message.content.split(" ")) == 3:
			role_name = message.content.split(" ")[2]
			
			if roles.find_one({"sid": message.server.id, "rolename": role_name}) is not None:
				role_id = roles.find_one({"sid": message.server.id, "rolename": role_name})["roleid"]
				role_object = discord.utils.get(message.server.roles, id=role_id)

				if role_object is not None:
					await client.remove_roles(message.author, role_object)
					await client.send_message(message.channel, "{} - role \"{}\" removed :ok_hand:".format(message.author.mention, role_name))

				else:
					await client.send_message("That role no longer exists on the server.")

			else:
				await client.send_message(message.channel, "That role doesn't exist.")

		else:
			await client.send_message(message.channel, "Invalid command syntax. See `!staibot help` for usage.")


	# Command to allow setting the notify role.
	if message.content.lower().startswith("!admin notifyrole"):
		# Check whether the user entered the role ID.
		if len(message.content.split(" ")) >= 3:
			# Store the entered role ID for nicer referencing later.
			role_id = message.content.split(" ")[2]
			
			# Check whether the user who issued the command is an administrator.
			if message.author.server_permissions.administrator:
				
				# Check whether the role exists in the server.
				role_exists = False
				for role in message.server.roles:
					if role.id == role_id:
						role_exists = True
				
				# If the role does exist:
				if role_exists:
					# Update it, or add it if it doesn't exist.
					print("Associating role id {} to server id {}.".format(role_id, message.server.id))
					roles.update({"sid": message.server.id}, {"sid": message.server.id, "rolename": "$notify", "roleid": role_id}, upsert=True)
					await client.send_message(message.channel, "Done :ok_hand:")
				
				else:
					await client.send_message(message.channel, "Role does not exist. Check the role ID and try again.")
			
			else:
				await client.send_message(message.channel, "{} - you don't have permission to do that.".format(message.author.mention))
		
		else:
			await client.send_message(message.channel, "Invalid command syntax. See `!staibot help` for usage.")

	# Command to allow adding roles.
	if message.content.lower().startswith("!admin addrole"):
		# Check whether there are enough arguments.
		if len(message.content.split(" ")) == 4:
			# Check whether the user who issued the command is an administrator.
			if message.author.server_permissions.administrator:
				role_name = message.content.split(" ")[2]
				role_id = message.content.split(" ")[3]
				
				# Check whether the role exists in the server.
				role_exists = False
				for role in message.server.roles:
					if role.id == role_id:
						role_exists = True

				if role_exists:
					if roles.find_one({"rolename": role_name}) == None:
						print("Adding role \"{}\" ({}) to server \"{}\".".format(role_name, role_id, message.server.name))
						roles.update({"sid": message.server.id, "rolename": role_name}, {"sid": message.server.id, "rolename": role_name, "roleid": role_id}, upsert=True)
						await client.send_message(message.channel, "Added role \"{}\" :ok_hand:".format(role_name))
					else:
						await client.send_message(message.channel, "A role with that name already exists.")
				
				else:
					await client.send_message(message.channel, "Role does not exist. Check the role ID and try again.")
			
			else:
				await client.send_message(message.channel, "{} - you don't have permission to do that.".format(message.author.mention))
		
		else:
			await client.send_message(message.channel, "Invalid command syntax. See `!staibot help` for usage.")

	# Command to allow deleting roles.
	if message.content.lower().startswith("!admin deleterole"):
		# Check whether there are enough arguments.
		if len(message.content.split(" ")) >= 3:
			# check whether the user who issued the command is an administrator.
			if message.author.server_permissions.administrator:
				role_name = message.content.split(" ")[2]
				# Check whether the role exists in the database.
				rdb_object = roles.find_one({"sid": message.server.id, "rolename": role_name})

				if rdb_object is not None:
					roles.delete_one({"sid": message.server.id, "rolename": role_name})
					await client.send_message(message.channel, "Role \"{}\" deleted. You may now delete the server role from within Discord.".format(role_name))
				
				else:
					await client.send_message(message.channel, "Cannot delete a role that doesn't exist. Use ```!role list``` to check.")
			
			else:
				await client.send_message(message.channel, "{} - you don't have permission to do this.")

		else:
			await client.send_message(message.channel, "Invalid command syntax. See `!staibot help` for usage.")

	# Command to list all relevant server information.
	if message.content.lower().startswith("!admin serverinfo"):
		if message.author.server_permissions.administrator:
			msg = "```"
			msg += "Server name: {}\n".format(message.server.name)
			msg += "Server ID: {}\n".format(message.server.id)
			msg += "Server roles:\n"
			for role in message.server.roles:
				msg += "    {} ({})\n".format(role.name, role.id)
			msg += "```"
			await client.send_message(message.author, msg)
		else:
			await client.send_message(message.channel, "{} - you don't have permission to do that.".format(message.author.mention))
