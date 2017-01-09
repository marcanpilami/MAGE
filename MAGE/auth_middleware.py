from django.contrib.auth.backends import RemoteUserBackend

class AzureAuthHeaderBackend(RemoteUserBackend):
    def clean_username(self, username):
        if len(username.split('#')) == 2:
            return username.split('#')[1]
        else:
            return username