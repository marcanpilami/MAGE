# coding: utf-8
""" Sample package checkers """

## Python imports
import os
from zipfile import ZipFile, BadZipfile

## Django imports
from django import forms

## MAGE imports
from scm.models import PackageCheckerBaseImpl


class DeliveryCheckerSql(PackageCheckerBaseImpl):
    description = 'Sample SQL delivery checker'

    def check(self, fileinfo, logical_component, installation_method):
        ## Must be a zip file
        try:
            zf = ZipFile(fileinfo)
            zf.testzip()
        except BadZipfile, e:
            raise forms.ValidationError(e)

        ## Must contain only SQL files either inside a 'scripts-sql' directory or at the root.
        for f in zf.namelist():
            s = f.strip('/').split('/') # zipfile read by Python's lib => always "/"
            if          (len(s) > 2) or \
                        (len(s) == 2 and s[0] != "scripts-sql") or \
                        (len(s) == 2 and os.path.splitext(s[1])[1] != '.sql') or \
                        (len(s) == 1 and not (s[0] == 'scripts-sql' or os.path.splitext(s[0])[1] == '.sql')):
                raise forms.ValidationError('Must only contain .sql files or a single "scripts-sql" directory containing .sql files')


        ## Encoding must be ISO-8859-1/ISO-8859-15/cp1252


        ## Done
        return

class DeliveryCheckerEar(PackageCheckerBaseImpl):
    description = 'Sample EAR delivery checker'

    def check(self, fileinfo, logical_component, installation_method):
        ## Must be a zip file
        try:
            zf = ZipFile(fileinfo)
            zf.testzip()
        except BadZipfile, e:
            raise forms.ValidationError('File is not an EAR archive or is corrupted: ' + str(e))

        ## Must end with 'ear'
        if os.path.splitext(fileinfo.name)[1] != '.ear':
            raise forms.ValidationError('Not an ear file')

        ## Done
        return

class DeliveryCheckerEarWar(PackageCheckerBaseImpl):
    description = 'Sample EAR or WAR delivery checker'

    def check(self, fileinfo, logical_component, installation_method):
        ## Must be a zip file
        try:
            zf = ZipFile(fileinfo)
            zf.testzip()
        except BadZipfile, e:
            raise forms.ValidationError('File is not an EAR or WAR archive or is corrupted: ' + str(e))

        ## Must end with 'ear'
        if os.path.splitext(fileinfo.name)[1] != '.ear' and os.path.splitext(fileinfo.name)[1] != '.war':
            raise forms.ValidationError('Not an ear or war file')

        ## Done
        return
