Security
##########

Access security
******************

By default MAGE gives everyone (anonymous users) read-only access to non-sensitive data. It means all projects, all environments.

A middleware can be enabled inside MAGE settings (a line to uncomment) in order to prevent anonymous access.

The following permissions are defined at project level and are always applied (even to anonymous users):

* sensitive data (fields marked as such in the component description, usually password-like fields) are only available to accounts with the `allfields_componentinstance` permission.
* uploading a new delivery requires the `modify_delivery` permission
* modifying an environment requires the `modify_project` permission

The following permissions are defined at project level and are only applied if not allowing anonymous access:

* viewing a project (including on the home page) requires the `view_project` permission


Super administrator accounts have access to everything without limitation.

The permissions above are specialized per project: one account can be allowed to see sensitive fields on one project and not on another.
There is also a set of permissions that are always applied to all the projects for which the user has the `modify_project` permission:

* `modify_delivery` allows to create and modify deliveries
* `install_installableset` allows to reference a new installation of a given package
* `del_backupset` allows to archive, unarchive a backup
* `validate_installableset` allows to validate a package or backupset
* `add_tag` allows to create , modify or remove a tag.
