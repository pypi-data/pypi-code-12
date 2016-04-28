import requests
import logging
import json
from .Project import *

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Account:

    """
    It represent your Mint-Labs Account. It implements also an HTTP connection with the server.
    Once it is instantiated  it will act as an identifier used by the rest of objects.

    :param username: username of the platform. To get one go to
                     https://platform.mint-labs.com

    :param password: the password assigned to the username.

    :param test: True -> connection will be done to the testing
                 platform (http://test.mint-labs.com).
                 False -> connection will be done to the platform
                 (http://platform.mint-labs.com).

    :type username: String
    :type password: String
    :type test: Bool

    """

    def __init__(self, username, password, test=False):
        self._cookie = None
        self._project_id = None
        self.username = username
        self.password = password
        if test:
            self.verify_certificates = False
            self.baseurl = "https://test.mint-labs.com"
        else:
            self.verify_certificates = True
            self.baseurl = "https://platform.mint-labs.com"
        self.login()

    def login(self):
        """Login to the platform."""
        content = self.send_request("login",
                                {"username": self.username, "password": self.password})
        if content["success"]:
            logging.info("Logged in as {0}".format(self.username))
            return True
        else:
            logging.error("Login is invalid")
            return False

    def logout(self):
        """
        Logout from the platform.

        :return: True if logout was successful, False otherwise.
        :rtype: Bool
        """

        content = self.send_request("logout")
        if content["success"]:
            logging.info("Logged out successfully")
            self._cookie = None
            return True
        else:
            logging.error("Logout was unsuccesful")
            return False

    def get_project(self, project_id):
        """
        Retrieve a project instance, given its id, which can be obtained
        checking account.projects.

        :param project_id: id of the project to retireve, either the numeric
                           id or the name
        :type project_id: Int or string

        :return: a project object representing the desired project
        :rtype: Project
        """
        if type(project_id) == int or type(project_id) == float:
            return Project(self, int(project_id))
        elif type(project_id) == str:
            projects = self.projects
            projects_match = [proj for proj in projects if proj['name'] == project_id]
            if not projects_match:
                raise Exception("Project {} does not exist or is not available for this user.".format(project_id))
            return Project(self, int(projects_match[0]["id"]))


    @property
    def projects(self):
        """
        List all the projects available to the current user.

        :return: List of project identifiers (strings)
        :rtype: List(Strings)
        """

        content = self.send_request("projectset_manager/get_projectset_list")
        if content.get("success", False):
            if len(content["data"]) > 0:
                titles = []
                for project in content["data"]:
                    titles.append({"name": project["name"], "id": project["_id"]})
                return titles
            else:
                logging.error("There are no projects.")
                return False
        else:
            logging.error("There was an error in the server.")
            return False

    def add_project(self, project_abbreviation, project_name, description="", users=[], from_date="", to_date=""):
        """
        Add a new project to the user account.

        :param project_abbreviation: Abbreviation of the project name.
        :param project_name: Project name.
        :param description: Description of the project.
        :param users: List of users to which this project is available.
        :param from_date: Date of beginning of the project.
        :param to_date: Date of ending of the project.

        :type project_abbreviation: String
        :type project_name: String
        :type description: String
        :type users: List(Strings)
        :type from_date: String
        :type to_date: String

        :return: True if project was correctly added, False otherwise
        :rtype: Bool

        """
        for project in self.projects:
            if project["name"] == project_name :
                logging.error("Project name or abbreviation already exists.")
                return False

        content = self.send_request(
            "projectset_manager/upsert_project",
            req_parameters={"name": project_name,
                            "description": description,
                            "from_date": from_date,
                            "to_date": to_date,
                            "abbr": project_abbreviation,
                            "users":"|".join(users)})
        if content.get("success", False):
            for project in self.projects:
                if project["name"] == project_name:
                    logging.info("Project was successfuly created.")
                    return Project(self, int(project["id"]))
            logging.error("Project could note be created.")
            return False
        else:
            logging.error("There was an error.")
            return False

    def send_request(self, path, req_parameters={}, req_headers={},
                      stream=False, return_raw_response=False):
        """
        Send a request to the Mint Labs Platform.

        Interaction with the server is performed as POST requests.

        :param req_url:  URL to perform the request. The host should be either
                         "https://test.mint-labs.com"
                         or "https://platform.mint-labs.com".

        :param req_parameters: data to send in the POST request.

        :param req_headers: "extra" headers to include in the request:
                            {"header-name": "value"}.
        :param stream: defer downloading the response body until accessing the
                       Response.content attribute.

        :param return_raw_response: When True, return the response from the server
                                    as-is. When False (by default), parse the
                                    answer as json to return a dictionary.

        :type req_url: String
        :type req_parameters: Dict
        :type req_headers: Dict
        :type stream: Bool
        :type return_raw_response: Bool
        """

        req_url = "{0}/{1}".format(self.baseurl, path)
        if self._cookie is not None:
            req_headers["Cookie"] = self._cookie
        req_headers["Mint-Api-Call"] = 1

        try:
            response = requests.post(req_url,
                                     data=req_parameters,
                                     headers=req_headers,
                                     timeout=900.0,
                                     stream=stream,
                                     verify=self.verify_certificates)
        except Exception as e:
            error = "Could not send request. ERROR: {0}".format(e)
            logging.error(error)
            raise Exception(error)

        # Set the login cookie in our object
        if "set-cookie" in response.headers:
            self._cookie = response.headers["set-cookie"]

        if return_raw_response:
            return response

        if response.status_code == 500:
            error = "Server returned status 500."
            logging.error(error)
            raise Exception(error)

        # raise exception if there is no response from server
        elif not response:
            error = "No response from server."
            logging.error(error)
            raise Exception(error)

        try:
            parsed_content = json.loads(response.text)
        except Exception as e:
            error = "Could not parse the response as JSON data: {}".format(response.text)
            logging.error(error)
            raise Exception(error)

        # If any other request is performed before login, raise an error
        if "error" in parsed_content:
            error = parsed_content["error"] or "Unknown error"
            logging.error(error)
            raise Exception(error)
        else:

            return parsed_content
