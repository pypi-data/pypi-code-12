# Pentaho endpoint constants



#############################################
# User Endpoint
#############################################

USERS_USERNAME_VAR = "userName"
USERS_PASSWORD_VAR = "password"

LIST_USERS = "list_users"
CREATE_USERS = "create_users"
DELETE_USERS = "delete_users"

PENTAHO_USER_ENDPOINT_DEFINITION = {
    CREATE_USERS: "/pentaho/api/userroledao/createUser",
    LIST_USERS: "/pentaho/api/users",
    DELETE_USERS: "/pentaho/api/userroledao/deleteUsers",
}
