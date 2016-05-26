import json, pickle

from base64 import b64encode, b64decode
from copy import copy


class PermissionsConfiguration():

	def __init__(self, is_registration_required=False):
		if type(is_registration_required) != bool:
			raise TypeError((
				"'is_registration_required' argument during instance creattion "
				"must be of boolean type"
				" - '%s' (%s) detected"
			) % (is_registration_required, type(is_registration_required)))
		else:
			self.__roles = set()
			self.__users = set()
			self.__actions = set()
			self.__conditions = set()
			self.__privileges = dict(
				for_users=dict(),
				for_roles=dict(),
			)
			self.__options = dict(
				is_registration_required=is_registration_required
			)

	###############################################################
	###############################################################
	# dump and load 
	###############################################################
	###############################################################

	def dumps(self):
		return json.dumps(dict(
			roles=list(self.__roles),
			users=list(self.__users),
			actions=list(self.__actions),
			conditions=list(self.__conditions),
			privileges=self.__privileges,
			options=self.__options,
		))

	def loads(self, dump_string):
		try:
			dump_dict = json.loads(dump_string)
		except ValueError as error:
			error.args = ("Invalid JSON format of dump_string",)
			raise
		else:
			# keep a backup of current state before starting to mangle the current state with __load()
			backup_dump_dict = json.loads(self.dumps())
			try:
				self.__load(dump_dict)
			except KeyError as error:
				self.__load(backup_dump_dict)
				raise

	def __load(self, dump_dict):
		self.__roles = set(dump_dict.pop("roles"))
		self.__users = set(dump_dict.pop("users"))
		self.__actions = set(dump_dict.pop("actions"))
		self.__conditions = set(dump_dict.pop("conditions"))
		self.__privileges = dump_dict.pop("privileges")
		self.__options = dump_dict.pop("options")
		if len(dump_dict) > 0:
			raise KeyError("Unknown keys %s found in dump dictionary" % dump_dict.keys())

	###############################################################
	###############################################################
	# registrations
	###############################################################
	###############################################################

	def is_registration_required(self, is_registration_required=None):
		if is_registration_required != None:
			if type(is_registration_required) != bool:
				raise TypeError((
					"'is_registration_required' argument must be of boolean type"
					" - '%s' (%s) detected"
				) % (is_registration_required, type(is_registration_required)))
			else:
				self.__options['is_registration_required'] = is_registration_required
		else:
			# return the current value
			return self.__options['is_registration_required']

	def register_roles(self, *args):
		for index, a_role in enumerate(args):
			if type(a_role) != str:
				raise TypeError((
					"%dth role (%s) for registering roles must be a string - '%s' detected"
				) % (index, a_role, type(a_role)))
			else:
				self.__roles.add(a_role)

	def register_users(self, *args):
		for index, a_user in enumerate(args):
			if type(a_user) != str:
				raise TypeError((
					"%dth user (%s) for registering users must be a string - '%s' detected"
				) % (index, a_user, type(a_user)))
			else:
				self.__users.add(a_user)

	def register_actions(self, *args):
		for index, an_action in enumerate(args):
			if type(an_action) != str:
				raise TypeError((
					"%dth action (%s) for registering actions must be a string - '%s' detected"
				) % (index, an_action, type(an_action)))
			else:
				self.__actions.add(an_action)

	def register_conditions(self, *args):
		for index, a_condition in enumerate(args):
			if type(a_condition) != str:
				raise TypeError((
					"%dth condition (%s) for registering conditions must be a string - '%s' detected"
				) % (index, a_condition, type(a_condition)))
			else:
				self.__conditions.add(a_condition)

	###############################################################
	###############################################################
	# assigning privileges
	###############################################################
	###############################################################

	def assign_privilege_for_a_role(self, a_role, an_action, is_allowed, a_condition=None):
		self.__validate_parameters(
			a_role=a_role, an_action=an_action, is_allowed=is_allowed, a_condition=a_condition
		)
		self.__privileges['for_roles'].setdefault(a_role, dict())
		self.__privileges['for_roles'][a_role].setdefault(an_action, False)
		self.__privileges['for_roles'][a_role][an_action] = self.__calibrate_action_privileges(
			self.__privileges['for_roles'][a_role][an_action], is_allowed, a_condition, 
		)

	def assign_privilege_for_a_user(self, a_user, an_action, is_allowed, a_condition=None):
		self.__validate_parameters(
			a_user=a_user, an_action=an_action, is_allowed=is_allowed, a_condition=a_condition
		)
		self.__privileges['for_users'].setdefault(a_user, dict())
		self.__privileges['for_users'][a_user].setdefault(an_action, False)
		self.__privileges['for_users'][a_user][an_action] = self.__calibrate_action_privileges(
			self.__privileges['for_users'][a_user][an_action], is_allowed, a_condition, 
		)

	def __validate_parameters(self, 
		a_role=None, a_user=None, an_action=None, 
		is_allowed=None, a_condition=None
	):
		if self.__options['is_registration_required']:
			if a_role and (a_role not in list(self.__roles)):
				raise LookupError("Role '%s' is not yet registered in this configuration" % a_role)

			if a_user and (a_user not in list(self.__users)):
				raise LookupError("User '%s' is not yet registered in this configuration" % a_user)

			if an_action and (an_action not in list(self.__actions)):
				raise LookupError("Action '%s' is not yet registered in this configuration" % an_action)

			if a_condition and (a_condition not in list(self.__conditions)):
				raise LookupError("Condition '%s' is not yet registered in this configuration" % a_condition)

		if is_allowed and (type(is_allowed) != bool):
			raise TypeError((
				"Value for is_allowed while assigning a privilege must be a boolean - '%s' detected"
			) % type(is_allowed))

	def __calibrate_action_privileges(self, action_privileges, is_allowed, a_condition):
		action_privileges = copy(action_privileges)
		if a_condition:
			if type(action_privileges) == dict:
				action_privileges[a_condition] = is_allowed
			else:
				action_privileges = {a_condition: is_allowed}
		else:
			action_privileges = is_allowed
		return action_privileges

	###############################################################
	###############################################################
	# determining privileges
	###############################################################
	###############################################################

	def is_allowed(self, invoker_role, invoker_user, requested_action, known_condition=None):
		user_privileges = self.__privileges['for_users'].get(invoker_user, False)
		if user_privileges:
			user_privileges_for_action = user_privileges.get(requested_action, False)
			if user_privileges_for_action:
				if type(user_privileges_for_action) == bool:
					return user_privileges_for_action
				else:
					# user_privileges_for_action is a dictionary of conditions
					return user_privileges_for_action.get(known_condition, False)
		role_privileges = self.__privileges['for_roles'].get(invoker_role, False)
		if role_privileges:
			role_privileges_for_action = role_privileges.get(requested_action, False)
			if role_privileges_for_action:
				if type(role_privileges_for_action) == bool:
					return role_privileges_for_action
				else:
					# role_privileges_for_action is a dictionary of conditions
					return role_privileges_for_action.get(known_condition, False)
		return False



