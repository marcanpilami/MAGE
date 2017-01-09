Azure deployment
#######################

Need :
* one MySQL database
* one empty Azure App service
* one AAD application

AAD environment
------------------

* Name: whatever. This will be displayed on login.
* Home page URL: https://magescm.azurewebsites.net (root of the app)
* Deconnection URL: none
* Type: Application/Web API
* Shared: no
* Callback URLs (change root): 
  * https://magescm.azurewebsites.net/openid/callback/login/
  * https://magescm.azurewebsites.net/openid/callback/logout/
* Generate a key.

App service
----------------

Disable:
* Python (yes!)
* PHP

Variables to create :

WEBSITE_PROTOCOL

AZURE_AD_CLIENT_ID (the "application ID in AAD UI")
AZURE_AD_CLIENT_SECRET (generated above)
AZURE_AD_DIRECTORY_GUID (directory itself -> Properties -> directory ID)

DEBUG (optional)

DB_ENGINE
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST




Remove all default documents.

No need to create handlers.

Finally, configure git deployment from https://github.com/marcanpilami/MAGE.git / Azure branch.
