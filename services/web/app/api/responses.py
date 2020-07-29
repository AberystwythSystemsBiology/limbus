def no_values_response():
    return {"success": False, "message": "No input data provided"}, 400


def validation_error_response(err):
    return {"success": False, "messages": err.messages}, 417


def transaction_error_response(err):
    try:
        return {"success": False, "message": str(err.orig.diag.message_primary)}, 417
    except Exception:
        return {"success": False, "message": str(err)}, 417


def success_with_content_response(content):
    return {"success": True, "content": content}, 200


def success_without_content_response():
    return {"success": True}, 200
