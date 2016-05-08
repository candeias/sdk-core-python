from requests import Request, Session
from mastercard.core.config import Config
from mastercard.core.constants import Constants
from mastercard.security.authentication import Authentication
from mastercard.core.exceptions import APIException, ObjectNotFoundException, InvalidRequestException, SystemException
import mastercard.core.util as util
import json
from ast import literal_eval


class APIController(object):


    ACTION_CREATE = "CREATE"
    ACTION_DELETE = "DELETE"
    ACTION_UPDATE = "UPDATE"
    ACTION_READ   = "READ"
    ACTION_LIST   = "LIST"
    ACTION_QUERY  = "QUERY"

    HTTP_METHOD_GET    = "GET"
    HTTP_METHOD_POST   = "POST"
    HTTP_METHOD_PUT    = "PUT"
    HTTP_METHOD_DELETE = "DELETE"

    KEY_ID     = "id"
    KEY_FORMAT = "Format"
    KEY_ACCEPT = "Accept"
    KEY_USER_AGENT = "User-Agent"
    KEY_CONTENT_TYPE = "Content-Type"
    APPLICATION_JSON = "application/json"
    PYTHON_SDK       = "Python_SDK"
    JSON             = "JSON"


    def __init__(self):

        #Set the parameters
        self.baseURL = Config.getAPIBaseURL()

        #Verify if the URL is correct
        if not util.validateURL(self.baseURL):
            raise APIException("URL: '" + self.baseURL + "' is not a valid url")


    def __check(self):
        """
        Check the pre-conditions before execute can be called
        """

        if Config.getAuthentication() is None or not isinstance(Config.getAuthentication(),Authentication):
            raise  APIException("No or incorrect authentication has been configured")


    def removeForwardSlashFromTail(self,text):
        """
        Removes the trailing / from url if any and returns the url
        """
        return text[:-1] if text.endswith("/") else text

    def getURL(self,action,resourcePath,inputMap):
        """
        Forms the complete URL by combining baseURL and replaced path variables in resourcePath from inputMap
        """

        #Remove the Trailing slash from base URL
        self.baseURL = self.removeForwardSlashFromTail(self.baseURL)

        #Remove the Trailing slash from the resource path
        resourcePath = self.removeForwardSlashFromTail(resourcePath)

        #Combine the  base URL and the path
        fullURL = self.baseURL + resourcePath

        #Replace the path variables
        fullURL = util.getReplacedPath(fullURL,inputMap)

        #This step is if id is in inputMap but was not specified in URL as /{id}
        #If the action is read,update or delete we add this id
        if APIController.KEY_ID in inputMap:
            if action.upper() in [APIController.ACTION_READ,APIController.ACTION_UPDATE,APIController.ACTION_DELETE]:
                fullURL += "/"+str(inputMap[APIController.KEY_ID])
                del inputMap[APIController.KEY_ID] #Remove from input path otherwise this would get add in query params as well

        return fullURL

    def getRequestObject(self,url,action,inputMap):
        """
        Gets the Request Object with URL and
        """
        #set action as upper for comparison
        action  = action.upper()
        #get method from action
        method  = self.getMethod(action)

        if method is None:
            raise APIException("Invalid action supplied: " + action);

        #Create the request object
        request = Request()

        #set the request parameters
        request.method = method
        request.url    = url
        request.headers[APIController.KEY_ACCEPT]       = APIController.APPLICATION_JSON
        request.headers[APIController.KEY_CONTENT_TYPE] = APIController.APPLICATION_JSON
        request.headers[APIController.KEY_USER_AGENT]   = APIController.PYTHON_SDK+"/"+Constants.VERSION

        #Add inputMap to params if action in read,delete,list,query
        if action in [APIController.ACTION_READ,APIController.ACTION_DELETE,APIController.ACTION_LIST,APIController.ACTION_QUERY]:
            request.params = inputMap
        elif action in [APIController.ACTION_CREATE,APIController.ACTION_UPDATE]:
            request.data = json.dumps(inputMap)

        #Set the query parameter Format as JSON
        request.params[APIController.KEY_FORMAT] = APIController.JSON

        return request


    def getMethod(self,action):

        actions = {
            APIController.ACTION_CREATE:APIController.HTTP_METHOD_POST,
            APIController.ACTION_DELETE:APIController.HTTP_METHOD_DELETE,
            APIController.ACTION_UPDATE:APIController.HTTP_METHOD_PUT,
            APIController.ACTION_READ:APIController.HTTP_METHOD_GET,
            APIController.ACTION_LIST:APIController.HTTP_METHOD_GET,
            APIController.ACTION_QUERY:APIController.HTTP_METHOD_GET
        }

        return actions.get(action.upper(),None)

    def execute(self,action,resourcePath,headerList,inputMap):

        #Check preconditions for execute
        self.__check()

        #Separate the headers from the inputMap
        headers = util.subMap(inputMap,headerList)

        fullURL = self.getURL(action,resourcePath,inputMap)
        request = self.getRequestObject(fullURL,action,inputMap)

        #Add headers
        for key, value in headers.iteritems():
            request.headers[key] = value

        #Sign the request
        #This should add the authorization header in the request
        Config.getAuthentication().signRequest(fullURL,request)
        prepreq = request.prepare()

        #Make the request
        sess = Session()
        response = sess.send(prepreq)

        content = response.content.decode("utf-8")
        return self.handleResponse(response,content)


    def handleResponse(self,response,content):
        status = response.status_code
        if 200 <= status <= 299:

            if content:
                try:
                    return json.loads(str(content))
                except ValueError:
                    return content
            else:
                 return ""
        elif 300 <= status <= 399:
            raise InvalidRequestException("Unexpected response code returned from the API causing redirect",status,content)
        elif status == 400:
            raise InvalidRequestException("Bad request",status,content)
        elif status == 401:
            raise APIException("You are not authorized to make this request",status,content)
        elif status == 403:
            raise APIException("You are not authorized to make this request",status,content)
        elif status == 404:
            raise ObjectNotFoundException("Object not found",status,content)
        elif status == 405:
            raise APIException("Operation not allowed",status,content)
        else:
            raise SystemException("Internal Server Error",status,content)
