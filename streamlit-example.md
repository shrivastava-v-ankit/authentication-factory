
# Example to use in Streamlit application for Microsoft OAuth2.0


## Usage

### Using authentication-factory
-----

**Note: For client information to be cached at server using extra_streamlit_components.**


```python
from authentication_factory.auth_factory import AuthFactory
import time
import extra_streamlit_components as stx

auth_config = {
    "state": "dada3534dfg", # Secret code for the application
    "tenant_id": "xxxxxxxxx", # Tenant ID of MS app service
    "client_id": "xxxxxx", # Client ID of MS app service
    "client_secret": "xxxx", # Client Secret value of MS app service
    "redirect_uri": "http://localhost:5000", # Streamlit applicatio URL
    "signout_uri": "http://localhost:5000/?logout=true" # Streamlit applicatio URL
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
    if "logout" in request_parameters and request_parameters["logout"] and request_parameters["logout"][0]:
        if request_parameters["logout"][0] in ["true"]:
            logout = True

    return (code, code_state, logout)


# fetch the cookie manger to read cookie value
def get_cookie_manager():
    return stx.CookieManager()


# fetch the user browser session value to be maintained for auth
def get_session_id():
    cookie_manager = get_cookie_manager()
    cookie_name = "ajs_anonymous_id"
    cookie_value = cookie_manager.get(cookie=cookie_name)

    return cookie_value


@authentication_factory_obj.login_handler()
def login_handler(*args, **kwargs):
    pass


@authentication_factory_obj.logout_handler()
def logout_handler(*args, **kwargs):
    pass


# We will send response_code and response_state in kwargs
@authentication_factory_obj.callback_handler()
def callback_handle(*args, **kwargs):
    pass


@st.cache_data(ttl=timedelta(hours=1))
def cache_auth_state():
    browser_sessions = st.session_state.get("authenticated_sessions", {})
    return browser_sessions


def application_code():
    print("your streamlit application code follows here")
    st.write(f"You are logged in as")


def authenticate():
    session_id = get_session_id()
    if session_id:
        _browser_sessions = cache_auth_state()

    _, _, logout = get_auth_code()
    if logout:
        if _browser_sessions and session_id in _browser_sessions:
            _browser_sessions.pop(session_id)

            st.session_state["authenticate"] = {}
            st.session_state["state"] = _browser_sessions["state"]
            st.session_state["authenticated_sessions"] = _browser_sessions

            cache_auth_state.clear()
            _sessions_obj = cache_auth_state()
            st.experimental_set_query_params()

    if _browser_sessions:
        st.session_state["authenticated_sessions"] = _browser_sessions

    if _browser_sessions and "state" in _browser_sessions and _browser_sessions["state"]:
        st.session_state["state"] = _browser_sessions["state"]

    if _browser_sessions and session_id in _browser_sessions and "authenticate" in _browser_sessions[session_id] and _browser_sessions[session_id]["authenticate"]:
        st.session_state["authenticate"] = _browser_sessions[session_id]["authenticate"]

    if "authenticated_sessions" not in st.session_state:
        st.session_state["authenticated_sessions"] = {
            "state": auth_config["state"]
        }
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

        if auth_dict and "display_name" in auth_dict and auth_dict["display_name"]:
            username = auth_dict["display_name"]
        if auth_dict and "expiry" in auth_dict and auth_dict["expiry"]:
            expiry = auth_dict["expiry"]
        if expiry:
            if int(expiry) >= int(time.time()):
                is_authenticated = True

    if not is_authenticated:
        response_code, response_state, _ = get_auth_code()

        if response_code and response_state:
            kwa = {
                "response_code": response_code,
                "response_state": response_state
            }
            result = callback_handle(kwargs=kwa)
            id_token = result.get("id_token", None)
            access_token = result.get("access_token", None)
            refresh_token = result.get("refresh_token", None)

            if id_token:
                authenticate_dict = {
                    "username": id_token["upn"],
                    "display_name": id_token["name"],
                    "expiry": id_token["exp"],
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
                st.session_state["authenticate"] = authenticate_dict
                st.session_state["authenticated_sessions"][session_id] = {
                    "authenticate": authenticate_dict
                }

                username = id_token["name"]
                is_authenticated = True

                cache_auth_state.clear()
                _sessions_obj = cache_auth_state()

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