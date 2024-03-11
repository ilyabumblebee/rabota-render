import requests
import json

url = "https://api.render.com/graphql"

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer rnd_zYodMdYwPDHVpFp32JvPhDJN4w90",
    "content-type": "application/json",
    "render-request-id": "b1a0b8fb-aee3-4fea-9977-24ff472d892f",
    "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site"
}

payload = json.dumps({
  "operationName": "submitSurveyResponse",
  "variables": {
    "surveyResponse": {
      "survey": "signup-survey",
      "content": {"primaryUse": "For clients", "projectType": "API / Mobile backend", "movingFrom": "Digital Ocean"}
    }
  },
  "query": "mutation submitSurveyResponse($surveyResponse: SurveyResponseInput!) {\n  submitSurveyResponse(surveyResponse: $surveyResponse)\n}\n"
})

response = session.post("https://api.render.com/graphql", headers=headers, data=payload)
print(response.text)
