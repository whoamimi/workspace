"""workspace/src/connectors.py"""


def check_kaggle_connection():
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    # api.set_config_value(name="username", value="bcookie11")
    api.authenticate()
    assert (
        api.get_config_value("username") is not None
    ), "No user is currently authenticated"
