import os
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from requests import RequestException

from lib import retry

GET_LAST_POSTS_QUERY = """
    query($postedAfter: DateTime) {
      posts(first: 100, postedAfter: $postedAfter, order:VOTES) {
        totalCount
        nodes {
          url
          name
          tagline
          description
        }
      }
    }
    """

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")


@retry([5, 30])
def get_bearer_token() -> str:
    resp = requests.post(
        "https://api.producthunt.com/v2/oauth/token",
        json={
            "client_id": API_KEY,
            "client_secret": API_SECRET,
            "grant_type": "client_credentials"
        },
        headers={"Content-Type": "application/json"}
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    raise RequestException(f"Failed: {resp.status_code}, {resp.text}")


@retry([5, 30, 90])
def execute_query(query: gql, client: Client, transport: RequestsHTTPTransport, variable_values: dict = None) -> dict:
    try:
        return client.execute(query, variable_values=variable_values)
    except Exception as e:
        if "invalid_token" in str(e) or "expired_token" in str(e):
            print("Token expired or invalid. Fetching a new token...")
            new_access_token = get_bearer_token()
            transport.headers["Authorization"] = f"Bearer {new_access_token}"
            return client.execute(query, variable_values=variable_values)
        else:
            raise e


def get_posts() -> (list, int):
    bearer_key = get_bearer_token()

    transport = RequestsHTTPTransport(
        url="https://api.producthunt.com/v2/api/graphql",
        headers={
            "Authorization": f"Bearer {bearer_key}",
            "Content-Type": "application/json"
        },
        use_json=True,
        retries=3,
        verify=True
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    posted_after = ((datetime.now(timezone.utc) - timedelta(days=1))
                    .replace(hour=18, minute=0, second=0, microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z"))
    variable_values = {"postedAfter": posted_after}
    query = gql(GET_LAST_POSTS_QUERY)

    response = execute_query(query, client, transport, variable_values=variable_values)
    total_count = response.get('posts', {}).get('totalCount', 0)
    posts = response.get('posts', {}).get('nodes', [])
    return posts, total_count
