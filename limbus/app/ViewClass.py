from flask import jsonify, wrappers


class ViewClass():

    def to_json(self) -> wrappers.Response:
        return jsonify(self.get_attributes())
