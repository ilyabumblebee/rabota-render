import requests
import json


def verify_email(session, token):
    data = {
        "operationName": "verifyEmail",
        "variables": {
            "token": token
        },
        "query": """
        mutation verifyEmail($token: String!) {
        verifyEmail(token: $token) {
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
        bitbucketId
        createdAt
        email
        featureFlags
        githubId
        gitlabId
        googleId
        name
        notifyOnPrUpdate
        otpEnabled
        passwordExists
        tosAcceptedAt
        intercomEmailHMAC
        __typename
        }
        """
    }
    response = session.post("https://api.render.com/graphql", json=data)
    return response
