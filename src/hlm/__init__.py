# -*- coding: utf8 -*-
# 高层功能封装类

from ._userapp import UserAppManager
from ._usersso import UserSSOManager
from ._usermsg import UserMsgManager
from ._userprofile import UserProfileManager

__all__ = ["UserAppManager", "UserSSOManager", "UserMsgManager", "UserProfileManager"]
