#!/usr/bin/env python3


if __name__ != 'tahoe.identity.backend':
    import sys, os
    sys.path = ['..'] + sys.path  #  os.path.join('..', '..')
    del sys, os
from tahoe import MongoBackend, IdentityBackend




class ImpossibleError(Exception):
   """This should not happend exception"""
   pass




class DAM(MongoBackend):
   """
   MongoBackend that implements ACL, uses a Identity Backend. Used just like a mongo backend with the exeption that a user hash must be used. 

   Notes
   -----
   For this DAM module to be useful it is recomended that the ident_backend argument has meaningful data,
      i.e, users, orgs and acl data.

   See Also:
   ---------
   MongoBackend: Mongo Backend
   """
   def__init(self, ident_backend, *args, **kwargs):
      """
      Parameters
      ----------
      ident_backend: IdentityBackend
         This should be of type Tahoe.IdentityBackend. This is where users, orgs, groups, are stored. This backend is used to pull and enforce access control.
      
      See Also
      --------
         User: User
         Org: Organization

      """

      self._ident_backend = ident_backend
      super().__init__(*args, **kwargs)




   def _get_groups_for_user(self, user_id):
      print("TODO: DAM._get_groups_for_user(): implement")
      return list() # empty untill the below code is enabled


      # groups_records = self._ident_backend.find({"itype": "object", 
      #                                 "sub_type": "cybexp_group",
      #                                 # may have to change below _acl fields name once group is implemented  
      #                                 "_acl": user_id}) 
      # belonging_gid = list()
      # for group in groups_records:
      #    belonging_gid.append(group["gid"]) # TODO question: group hash doesnt seem to be good idea since if group changes then so does hash, then we need to update acl fields

      # return belonging_gid

   def _get_acl_for_user(self, user_id):
      """Returns the organizations IDs that the user(of `user_id`) has acces to. That is, the user is either in the organization's ACL,
            the user belongs to a group that is in the organizations ACL, or the user has matched a rule or wildcard rule in the organizations ACL.
      Returns
      -------
      expanded_acl: list
         List of organization IDs that the user with `user_id` has access to.
      """


      # check direct access to org's data, user directly in orgs acl
      direct_acl_orgs = self._ident_backend.find({"itype": "object", 
                                      "sub_type": "cybexp_org", 
                                      "_acl": user_id})
      direct_access = list()
      for org in direct_acl_orgs:
         direct_access.append(org["orgid"]) # TODO check that orgid is what we need for acl

      # # check indirect access to org's data, user belongs to a groupd that has access to org data
      # users_groups = self._get_groups_for_user(user_id)
      # indirect_acl_orgs = self._ident_backend.find({"itype": "object", 
      #                                 "sub_type": "cybexp_org", 
      #                                 "_acl": users_groups})
      # indirect_access = list()
      # for org in indirect_acl_orgs:
      #    indirect_access.append(org["orgid"]) # TODO check that orgid is what we need for acl
      
      # TODO generate list of orgs that this user has access to only based on their rules
      #rule_access = list() # list of orgs

      expanded_acl = direct_access #+ indirect_access + rule_access

      return expanded_acl 

   def DAM_find_decorator(func):
      """
      Decorator that enforces ACL when doing query/find operations.

      """
      def wrapper(self, user_id, *args, **kwargs):
         """ Will use `user_id` to find which organization the use has read access to, then it will modify `args[0]`(the query) and apply the acl restrictions.
               It will do so by editing the query before calling the decorated function `func`. This decorator is for find/query operations only, not insert operations.
         Parameter
         ---------
         user_id: str
            hash of the user that is quering the data
         """
         
    
         query = args[0]

         if 'orgid' in query:
            raise ImpossibleError
    
         allowed_orgs = self._get_acl_for_user(user_hash)

         acl_query = {"orgid": {"$in": allowed_orgs}} # TODO orgs._hash
    
         new_query = query.update(acl_query) # {**query, **acl_query}

         args[0] = new_query
    
         result = func(self, *args, **kwargs)
         return result

      return wrapper

   @DAM_find_decorator
   def find(self, *args, **kwargs):
      """Calls parent's (MongoBackend) find() function, enforcing access control restrictions defined based on acl in orgs.
      """
      return super().find(self, *args,**kwargs)

   @DAM_find_decorator
   def find_one(self, *args, **kwargs):
      """Calls parent's (MongoBackend) find_one() function, enforcing access control restrictions based on acl in orgs.
      """
      return super().find_one(*args,**kwargs)




   # def DAM_insert_decorator(func):
   #    def wrapper(self, *args, **kwargs):
   #       print("TODO DAM insert decorator")
   #       # TODO this decorator
   #       result = func(self, *args, **kwargs)
   #       return result

   # @DAM_insert_decorator
   # def insert(self, *args, **kwargs):
   #    pass

   # 