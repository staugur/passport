# -*- coding: utf-8 -*-
"""
    passport.views.AdminView
    ~~~~~~~~~~~~~~

    The blueprint for admin view.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from flask import Blueprint, request, render_template, jsonify, g, abort, redirect, url_for, flash
from utils.web import adminlogin_required

AdminBlueprint = Blueprint("admin", __name__)

@AdminBlueprint.route("/")
@adminlogin_required
def index():
    return render_template("admin/index.html")
