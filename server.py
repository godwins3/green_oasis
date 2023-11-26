import logging
import os

import flask
from flask import request
from flask import Response
from flask_cors import CORS, cross_origin

from go_config import *

from checkers import check_token
from users.persistence import get_user_info