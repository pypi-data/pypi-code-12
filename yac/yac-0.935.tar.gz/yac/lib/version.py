import requests, jmespath

# for the registry find, find the latest version of the app input, in the container org input
def get_latest_version(app, container_org, registry_url='https://registry.hub.docker.com'):

    # endpoint use to determine the latest version in the registry input for this app
    endpoint_uri = "/v2/repositories/%s/%s/tags"%(container_org,app)

    # hit the endpoint
    endpoint_response = requests.get(registry_url + endpoint_uri) 

    # use jmespath to extract just the version value for each
    versions = jmespath.search("results[*].name",endpoint_response.json())

    # jmespath leaves a weird prefix on each result. remove by str conversion
    latest_version = "not found!"

    if versions:

        versions = [str(i) for i in versions]

        latest_version = ""

        if (versions and len(versions)>=1):

            if 'latest' in versions:

                latest_version = "latest"
            
            else:
                
                # sort and grab the last value in the resulting list (the latest version)
                versions.sort()
                latest_version = versions[-1]

    return str(latest_version)

def get_app_version(app_alias, my_service_descriptor):

    app_version = ""

    # the version would be in the image for this app
    search_str = "task-definition.containerDefinitions[?name=='%s'].image"%app_alias
    images_found = jmespath.search(search_str, my_service_descriptor)

    if images_found and len(images_found)==1:

        # grab the version from the tail end of the image label
        app_version = str(images_found[0]).split(':')[-1]

    return app_version    