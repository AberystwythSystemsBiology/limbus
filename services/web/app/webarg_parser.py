# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import abort
from webargs import core
from webargs.flaskparser import FlaskParser
import re


def _structure_dict(dict_):
    def structure_dict_pair(r, key, value):
        m = re.match(r"(\w+)\.(.*)", key)
        if m:
            if r.get(m.group(1)) is None:
                r[m.group(1)] = {}
            structure_dict_pair(r[m.group(1)], m.group(2), value)
        else:

            r[key] = value

    r = {}
    for k, v in dict_.items():
        structure_dict_pair(r, k, v)
    return r


class NestedQueryFlaskParser(FlaskParser):
    def load_querystring(self, req, schema):
        return _structure_dict(req.args)


parser = NestedQueryFlaskParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs

# This error handler is necessary for usage with Flask-RESTful
@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(417, {"message": err.messages})


error_handler = parser.error_handler
