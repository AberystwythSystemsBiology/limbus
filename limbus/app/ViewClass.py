from flask import jsonify, wrappers


class ViewClass():
    def __init__(self):
        self.db_sessions = {}

    def get_attributes(self):
        return {}

    def to_json(self) -> wrappers.Response:
        return jsonify(self.get_attributes())
