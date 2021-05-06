"""
Errors related to Users, Orgs and Input config.
"""

class AdminIsNotUserError(Exception):
    pass

class InvalidUserHashError(Exception):
    pass

class OrgExistsError(ValueError):
    """The orgname already exists in DB."""
    pass

class PasswordError(Exception):
    pass

class UserError(Exception):
    pass

class UserExistsError(ValueError):
    """The username(email) already exists in DB."""
    pass

class UserIsAdminError(Exception):
    pass

class UserIsInAclError(Exception):
    pass

class UserIsNotAdminError(Exception):
    pass

class UserIsNotInAclError(Exception):
    pass

class UserIsNotInOrgError(Exception):
    pass

class UserIsInOrgError(Exception):
    pass

class UserIsOnlyAdminError(Exception):
    pass
