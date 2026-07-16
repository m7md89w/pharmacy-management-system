import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 10


# ==========================================
# HEADERS
# ==========================================
def get_headers(token=None):

    headers = {
        "Content-Type": "application/json"
    }

    if token:
        headers["Authorization"] = (
            f"Bearer {token}"
        )

    return headers


# ==========================================
# HANDLE RESPONSE
# ==========================================
def handle_response(response):

    if response.status_code >= 500:
        raise Exception(
            "Backend server error."
        )

    return response


# ==========================================
# GET
# ==========================================
def get(endpoint, token=None):

    try:
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=get_headers(token),
            timeout=TIMEOUT
        )

        return handle_response(
            response
        )

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Cannot connect to Backend Server."
        )

    except requests.exceptions.Timeout:
        raise Exception(
            "Request timeout."
        )

    except requests.exceptions.RequestException as e:
        raise Exception(str(e))


# ==========================================
# POST
# ==========================================
def post(endpoint, data, token=None):

    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers=get_headers(token),
            timeout=TIMEOUT
        )

        return handle_response(
            response
        )

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Cannot connect to Backend Server."
        )

    except requests.exceptions.Timeout:
        raise Exception(
            "Request timeout."
        )

    except requests.exceptions.RequestException as e:
        raise Exception(str(e))


# ==========================================
# PUT
# ==========================================
def put(endpoint, data=None, token=None):

    try:
        response = requests.put(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers=get_headers(token),
            timeout=TIMEOUT
        )

        return handle_response(
            response
        )

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Cannot connect to Backend Server."
        )

    except requests.exceptions.Timeout:
        raise Exception(
            "Request timeout."
        )

    except requests.exceptions.RequestException as e:
        raise Exception(str(e))


# ==========================================
# PATCH
# ==========================================
def patch(endpoint, data=None, token=None):

    try:
        response = requests.patch(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers=get_headers(token),
            timeout=TIMEOUT
        )

        return handle_response(
            response
        )

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Cannot connect to Backend Server."
        )

    except requests.exceptions.Timeout:
        raise Exception(
            "Request timeout."
        )

    except requests.exceptions.RequestException as e:
        raise Exception(str(e))


# ==========================================
# DELETE
# ==========================================
def delete(endpoint, token=None):

    try:
        response = requests.delete(
            f"{BASE_URL}{endpoint}",
            headers=get_headers(token),
            timeout=TIMEOUT
        )

        return handle_response(
            response
        )

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Cannot connect to Backend Server."
        )

    except requests.exceptions.Timeout:
        raise Exception(
            "Request timeout."
        )

    except requests.exceptions.RequestException as e:
        raise Exception(str(e))


# ==========================================
# FILE UPLOAD
# ==========================================
def post_file(
    endpoint,
    files,
    token=None
):

    try:

        headers = {}

        if token:
            headers["Authorization"] = (
                f"Bearer {token}"
            )

        response = requests.post(
            f"{BASE_URL}{endpoint}",
            files=files,
            headers=headers,
            timeout=TIMEOUT
        )

        return handle_response(
            response
        )

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Cannot connect to Backend Server."
        )

    except requests.exceptions.Timeout:
        raise Exception(
            "Request timeout."
        )

    except requests.exceptions.RequestException as e:
        raise Exception(str(e))