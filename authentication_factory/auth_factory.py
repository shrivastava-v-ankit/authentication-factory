from .auth_decorators import AuthDecorators
from functools import wraps


class AuthFactory(object):
    def __init__(self, auth_type, config) -> None:
        self.auth_type = auth_type
        self.auth_obj = self.get_auth()
        self.config = config

    def get_auth(self):
        if self.auth_type in ["ms-oauth2"]:
            from .auth.ms_oauth2 import MS_OAuth2
            return MS_OAuth2()

    def login_handler(self):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                @self.auth_obj.login_handler(config=self.config)
                def login_handler(*args, **kwargs):
                    assert ("auth_url" in kwargs)
                    return kwargs["auth_url"]
                result = login_handler()

                # kwargs["auth_url"] = result
                _result = f(*args, **kwargs)
                return result
            return wrapper
        return decorator

    def logout_handler(self):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                @self.auth_obj.logout_handler(config=self.config)
                def logout_handler(*args, **kwargs):
                    assert ("logout_uri" in kwargs)
                    return kwargs["logout_uri"]
                result = logout_handler()

                # kwargs["logout_uri"] = result
                _result = f(*args, **kwargs)
                return result
            return wrapper
        return decorator

    def callback_handler(self, response_code: str, response_state: str):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                @self.auth_obj.callback_handler(config=self.config,
                                                response_code=response_code,
                                                response_state=response_state)
                def callback_handler(*args, **kwargs):
                    assert ("id_token" in kwargs)
                    return kwargs["id_token"]
                result = callback_handler()

                # kwargs["id_token"] = result
                _result = f(*args, **kwargs)
                return result
            return wrapper
        return decorator
