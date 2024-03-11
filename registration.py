import requests


def sign_up_user(session, email, password, captchaToken):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    session.headers.update(headers)
    body = {
        "operationName": "signUp",
        "variables": {
            "signup": {
                "email": email,
                "password": password,
                "newsletterOptIn": False,
                "hcaptchaToken": captchaToken
            }
        },
        "query": """mutation signUp($signup: SignupInput!) {
          signUp(signup: $signup) {
            ...authResultFields
            __typename
          }
        }

        fragment authResultFields on AuthResult {
          idToken
          expiresAt
          user {
            ...userFields
            sudoModeExpiresAt
            __typename
          }
          readOnly
          __typename
        }

        fragment userFields on User {
          id
          active
          createdAt
          email
          passwordExists
          tosAcceptedAt
          __typename
        }"""
    }
    response = session.post("https://api.render.com/graphql", json=body, headers=headers)
    if response.ok:
        response_json = response.json()
        if ("data" in response_json and
            response_json["data"].get("signUp") is not None and
            "user" in response_json["data"]["signUp"] and
            response_json["data"]["signUp"]["user"].get("id") and
            response_json["data"]["signUp"]["user"].get("email") == email):
            return 200, session
    print(response.text)
    return 429, session
