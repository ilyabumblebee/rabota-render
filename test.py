import requests
import json


# headers = {
#     "accept": "*/*",
#     "accept-language": "en-US,en;q=0.9",
#     "content-type": "application/json",
#     "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\"",
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": "\"Windows\"",
#     "sec-fetch-dest": "empty",
#     "sec-fetch-mode": "cors",
#     "sec-fetch-site": "same-site"
# }

def verify_email(token):
    data = {
        "operationName": "verifyEmail",
        "variables": {
            "token": "3DZfB5G3Vzci1jbm5pZjZpMWhibHM3MzlsOXQwZwU_NGNSRNoJAHmgj78q706w9RHiKea77SL1SAUVznpK"
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
    response = requests.post("https://api.render.com/graphql", json=data)
