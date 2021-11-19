"""
User Stuffs
"""

# User Database (Currently only store in memory)
__userdb = []


class User:
    """
    User model
    """
    uid = ''        # user id (identity)

    # enter some other information here...
    state = 0       # state of that user

    def __init__(self, userid):
        super().__init__()
        self.uid = userid
        self.state = 0


def getuser(userid) -> User:
    """
    Get user data by User ID,
    """
    for u in __userdb:
        if u.uid == userid:
            return u
    print("[Create User Data] User ID=", userid)
    new_user = User(userid)
    __userdb.append(new_user)
    return new_user
