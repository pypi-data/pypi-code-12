# Pentaho endpoint constants


#############################################
# User Endpoint
#############################################

PENTAHO_USERS_ENDPOINT_API = "users"

USERS_USERNAME_VAR = "userName"
USERS_PASSWORD_VAR = "password"

USERS_NEW_PASSWORD_VAR = "newPassword"
USERS_OLD_PASSWORD_VAR = "oldPassword"
USERS_DELETE_VAR = "userNames"

LIST_USERS = "list_users"
CREATE_USERS = "create_users"
DELETE_USERS = "delete_users"
CHANGE_USER_PASSWORD = "change_user_password"

TAB_SEPARATOR = '\t'

# see documentation here https://help.pentaho.com/Documentation/6.0/0R0/070/010/0D0/0O0
PENTAHO_USER_ENDPOINT_DEFINITION = {
    CREATE_USERS: ("put", "/pentaho/api/userroledao/createUser"),
    LIST_USERS: ("get", "/pentaho/api/userroledao/users"),
    DELETE_USERS: ("put", "/pentaho/api/userroledao/deleteUsers"),
    CHANGE_USER_PASSWORD: ("put", "/pentaho/api/userroledao/user")
}

#############################################
# Role Endpoint
#############################################

PENTAHO_ROLES_ENDPOINT_API = "roles"

ROLES_ASSIGN_VAR = "roleNames"

GET_ROLES_FOR_USER = "list_user_roles"
ASSIGN_ROLE_TO_USER = "assign_role_to_user"
REMOVE_ROLE_FROM_USER = "remove_role_from_user"

PENTAHO_ROLE_ENDPOINT_DEFINITION = {
    GET_ROLES_FOR_USER: ("get", "/pentaho/api/userroledao/userRoles"),
    ASSIGN_ROLE_TO_USER: ("put", "/pentaho/api/userroledao/assignRoleToUser"),
    REMOVE_ROLE_FROM_USER: ("put", "/pentaho/api/userroledao/removeRoleFromUser")
#     CREATE_ROLE: "/pentaho/api/userroledao/createRole",
#     DELETE_ROLE: "/pentaho/api/userroledao/deleteRoles",
#     LIST_ROLES: "/pentaho/api/userroledao/roles",
#     LIST_MEMBERS_ROLE: "/pentaho/api/userroledao/roleMembers",
#     ASSIGN_PERM_TO_ROLE: "/pentaho/api/userroledao/roleAssignments",
#     LIST_PERM_FOR_ROLE: "/pentaho/api/userroledao/logicalRoleMap",
}


#############################################
# Pentaho class constant
#############################################

PENTAHO_BASIC_AUTH = 'basic'
PENTAHO_COOKIE_AUTH = 'cookie'
PENTAHO_DEFAULT_COOKIE_NAME = 'JSESSIONID'

PENTAHO_AVAILABLE_ENDPOINT_TYPE = {
    PENTAHO_USERS_ENDPOINT_API: PENTAHO_USER_ENDPOINT_DEFINITION,
    PENTAHO_ROLES_ENDPOINT_API: PENTAHO_ROLE_ENDPOINT_DEFINITION
}
