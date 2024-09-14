import os

import requests
from dotenv import load_dotenv
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from requests import RequestException

from lib import retry

load_dotenv()


@retry([5, 30])
def get_bearer_token(*, client_id: str, client_secret: str) -> str:
    resp = requests.post(
        "https://api.producthunt.com/v2/oauth/token",
        json={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        },
        headers={"Content-Type": "application/json"}
    )
    if resp.status_code == 200:
        print(f"Status Code: {resp.status_code}, Response: {resp.text}")
        return resp.json().get("access_token")
    raise RequestException(f"Failed: {resp.status_code}, {resp.text}")


if __name__ == '__main__':
    # get Bearer token
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")
    bearer_key = get_bearer_token(client_id=API_KEY, client_secret=API_SECRET)
    print("bearer_key", bearer_key)

    # run request
    transport = RequestsHTTPTransport(
        url="https://api.producthunt.com/v2/api/graphql",
        headers={
            "Authorization": f"Bearer {bearer_key}"
        },
        use_json=True,
        retries=3,
        verify=True
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql("""
    {
      posts(first: 1) {
        edges {
          node {
            id
            name
          }
        }
      }
    }
    """)

    try:
        response = client.execute(query)
        print("response", response.keys(), response.values())
    except Exception as e:
        print(f"GraphQL query failed: {e}")
