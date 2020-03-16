
import json

from bson import json_util

from flask.json import JSONEncoder


class MongoJSONEncoder(JSONEncoder):
    def default(self, o):
        return json.loads(json.dumps(o, default=json_util.default))
