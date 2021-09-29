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


def not_found(entity=""):
    return (
        {"success": False, "message": "Instance %s not found" % entity},
        404,
        {"ContentType": "application/json"},
    )

def sample_assigned_delete_response():
    return(
        {"success": False, "message":"Can't delete assigned samples"},
        400,
        {"ContentType":"application/json"}
    )

def in_use_response(entity=""):
    return(
        {"success": False, "message":"Has associated " + entity},
        400,
        {"ContentType":"application/json"}
    )

def no_values_response():
    return (
        {"success": False, "message": "No input data provided"},
        400,
        {"ContentType": "application/json"},
    )

def locked_response(entity=""):
    return({"success": False, "message": "Entity %s is locked" % entity},
            400,
            {"ContentType": "application/json"})


def invalid_query_response():
    return (
        {"success": False, "message": "No parsable query data provided"},
        400,
        {"ContentType": "application/json"},
    )


def validation_error_response(err):
    try:
        message = err.messages

    except AttributeError:
        if "messages" in err.keys():
            message = err["messages"]
        else:
            message = err

    return (
        {"success": False, "message": message, "type": "Validation Error"},
        417,
        {"ContentType": "application/json"},
    )


def transaction_error_response(err):
    try:
        return (
            {"success": False, "message": str(err.orig.diag.message_primary)},
            417,
            {"ContentType": "application/json"},
        )
    except Exception:
        return (
            {"success": False, "message": str(err), "type": "Transaction Error"},
            417,
            {"ContentType": "application/json"},
        )


def not_allowed():
    return (
        {
            "success": True,
            "message": "Naughty naughty, you're not supposed to be here.",
        },
        401,
        {"ContentType": "application/json"},
    )


def success_with_content_response(content):
    return (
        {"success": True, "content": content},
        200,
        {"ContentType": "application/json"},
    )

def success_with_content_message_response(content, message=""):
    return (
        {"success": True, "content": content, "message": message},
        200,
        {"ContentType": "application/json"},
    )


def success_without_content_response():
    return {"success": True}, 200, {"ContentType": "application/json"}


def prepare_for_chart_js(a):
    ye = {"labels": [], "data": []}

    for (label, data) in a:
        ye["labels"].append(label)
        ye["data"].append(data)

    return ye
