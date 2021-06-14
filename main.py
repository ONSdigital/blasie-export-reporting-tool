from app.app import app, load_config
from extract_mi_call_history import import_mi_call_history
from upload_call_history import add_call_history_to_datastore
from import_call_history import import_call_history_data
from models.config import Config


def upload_call_history(_event, _context):
    config = Config.from_env()
    config.log()

    merged_call_history = import_call_history_data(config)

    status = add_call_history_to_datastore(merged_call_history)
    print(status)

    return status


def mi_call_history(_event, _context):
    config = Config.from_env()
    config.log()

    merged_call_history = import_mi_call_history(config)

    print(merged_call_history)

    return merged_call_history


load_config(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011)
