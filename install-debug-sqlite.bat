@echo off

rem Script d'installation et r‚installation de MAGE
rem Script pour Windows 7/Vista/XP


echo ***********************************************************
echo ** Installation de MAGE
echo ***********************************************************
echo.
echo.

rem Check: python
echo V‚rification de la pr‚sence de Python
python -V
IF %ERRORLEVEL% NEQ 0 goto errPython
echo ***Python d‚tect‚

rem Check: Django
echo.
echo V‚rification de la pr‚sence de Django
python -c "import django"
IF %ERRORLEVEL% NEQ 0 goto errDjango
echo ***Django d‚tect‚

rem Supression de la base de donn‚es si d‚j… pr‚sente
IF EXIST django.db del django.db

rem Installation de la base
echo.
echo Installation de la base
python manage.py syncdb --noinput
IF %ERRORLEVEL% NEQ 0 goto errSync
echo ***Base install‚e


rem Cr‚ation super user
python manage.py loaddata default_super_user.json
IF %ERRORLEVEL% NEQ 0 goto errSU
echo ***Super utilisateur cr‚‚


rem Objets de test
echo.
echo Population de la base avec des objets de test
python populate.py
IF %ERRORLEVEL% NEQ 0 goto errPop
echo ***Objets copi‚s

rem Fin du script
GOTO end




:errPython
echo Python non install‚ ou absent du PATH - installation annul‚e
GOTO END

:errDjango
echo Django non install‚ - installation annul‚e
GOTO END

:errSync
echo Erreur lors de la cr‚ation de la base - v‚rifiez le mod‡le
GOTO END

:errSU
echo Erreur cr‚ation super utilisateur - la base est n‚anmoins install‚e
GOTO END

:errPop
echo Erreur lors du remplissage de la base. MAGE est n‚anmoins install‚.
GOTO END

:END
echo.
echo Fin de l'installation.
