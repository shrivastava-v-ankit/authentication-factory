
# Example to use in Streamlit application for Microsoft OAuth2.0


## Usage

### Using authentication-factory
-----
```python
from authentication_factory.auth_factory import AuthFactory

auth_config = {
    "state": "dada3534dfg", # Secret code for the application
    "tenant_id": "xxxxxxxxx", # Tenant ID of MS app service
    "client_id": "xxxxxx", # Client ID of MS app service
    "client_secret": "xxxx", # Client Secret value of MS app service
    "redirect_uri": "http://localhost:5000", # Streamlit applicatio URL
    "signout_uri": "http://localhost:5000" # Streamlit applicatio URL
}

authentication_factory_obj = AuthFactory(auth_type=auth_config"auth_type"], config=auth_config)

def get_auth_code():
    request_parameters = st.experimental_get_query_params()
    code_state = None
    code = None

    if "state" in request_parameters and request_parameters["state"] and request_parameters["state"][0]:
        code_state = request_parameters["state"][0]
    if "code" in request_parameters and request_parameters["code"] and request_parameters["state"][0]:
        code = request_parameters["code"][0]

    return (code, code_state)


response_code, response_state = get_auth_code()

@authentication_factory_obj.login_handler()
def login_handler(*args, **kwargs):
    pass


@authentication_factory_obj.logout_handler()
def logout_handler(*args, **kwargs):
    pass


@authentication_factory_obj.callback_handler(response_code=response_code, response_state=response_state)
def callback_handle(*args, **kwargs):
    pass


@st.cache_data(ttl=timedelta(hours=1))
def cache_auth_state():
    state = st.session_state.get("state", None)
    authenticate_dict = st.session_state.get("authenticate", {})

    return state, authenticate_dict


def application_code():
    print("your streamlit application code follows here")


def authenticate():
    cache_state, cache_auth = cache_auth_state()
    if cache_state:
        st.session_state["state"] = cache_state

    if cache_auth:
        st.session_state["authenticate"] = cache_auth

    if "state" not in st.session_state:
        st.session_state["state"] = auth_config["state"]

    is_authenticated = False
    username = None

    # First check the state and the expiry of the auth
    if "authenticate" in st.session_state:
        # #if not state
        # ##Go to auth
        # #if state and expired
        # ##Go to auth
        auth_dict = st.session_state.get("authenticate")
        expiry = None

        if auth_dict and "username" in auth_dict and auth_dict["username"]:
            username = auth_dict["username"]
        if auth_dict and "expiry" in auth_dict and auth_dict["expiry"]:
            expiry = auth_dict["expiry"]
        if expiry:
            if int(expiry) >= int(time.time()):
                is_authenticated = True

    if not is_authenticated:
        global response_code
        global response_state
        response_code, response_state = get_auth_code()

        if response_code and response_state:
            id_token = callback_handle()
            if id_token:
                authenticate_dict = {
                    "username": id_token["upn"],
                    "display_name": id_token["name"],
                    "expiry": id_token["exp"]
                }
                st.session_state["authenticate"] = authenticate_dict
                username = id_token["name"]
                is_authenticated = True
                cache_auth_state.clear()
                cache_auth_state()
                st.experimental_set_query_params()

    if not is_authenticated:
        auth_url = login_handler()
        st.write(
            f'''<div style="text-align: right;font-size:20px; font-weight: 300; line-height: 0.1;letter-spacing: -0.005em; font-family: "Source Sans Pro", sans-serif";><a target="_self" href="{auth_url}">Login</a></div>''', unsafe_allow_html=True)
    else:
        logout_url = logout_handler()
        st.write(
            f'''<div style="text-align: right;font-size:20px; font-weight: 300; line-height: 0.1;letter-spacing: -0.005em; font-family: "Source Sans Pro", sans-serif";><a target="_self" href="{logout_url}" title="{username}">Logout</a></div>''', unsafe_allow_html=True)
        application_code()
```