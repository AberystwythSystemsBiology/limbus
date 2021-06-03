# Copyright (C) 2021 Keiron O'Shea <keo7@aber.ac.uk>
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

# Decided that it'd be nice to have some form of type hinting, this Union
# annotation represents all possible Flask views. Unfortunately, Flask doesn't
# return any any type hinting - so this sorta does it.

import typing
from werkzeug.datastructures import Headers
from werkzeug.wrappers import BaseResponse

_str_bytes = typing.Union[str, bytes]
_data_type = typing.Union[
    _str_bytes,
    BaseResponse,
    typing.Dict[str, typing.Any],
    typing.Callable[
        [
            typing.Dict[str, typing.Any],
            typing.Callable[[str, typing.List[typing.Tuple[str, str]]], None],
        ],
        typing.Iterable[bytes],
    ],
]

_status_type = typing.Union[int, _str_bytes]
_headers_type = typing.Union[
    Headers,
    typing.Dict[_str_bytes, _str_bytes],
    typing.Iterable[typing.Tuple[_str_bytes, _str_bytes]],
]

flask_return_union = typing.Union[
    _data_type,
    typing.Tuple[_data_type],
    typing.Tuple[_data_type, _status_type],
    typing.Tuple[_data_type, _headers_type],
    typing.Tuple[_data_type, _status_type, _headers_type],
]
