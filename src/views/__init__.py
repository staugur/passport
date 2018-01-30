# -*- coding: utf8 -*-
# views blueprint

from .FrontView import FrontBlueprint
from .AdminView import AdminBlueprint
from .ApiView import ApiBlueprint

__all__ = ["FrontBlueprint", "AdminBlueprint", "ApiBlueprint"]
