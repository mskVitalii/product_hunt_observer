import os
from datetime import datetime, timezone

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
        return resp.json().get("access_token")
    raise RequestException(f"Failed: {resp.status_code}, {resp.text}")


@retry([5, 30, 90])
def execute_query(query: gql, client: Client, transport: RequestsHTTPTransport, variable_values: dict = None) -> dict:
    try:
        return client.execute(query, variable_values=variable_values)
    except Exception as e:
        if "invalid_token" in str(e) or "expired_token" in str(e):
            print("Token expired or invalid. Fetching a new token...")
            new_access_token = get_bearer_token(
                client_id=os.getenv("API_KEY"),
                client_secret=os.getenv("API_SECRET")
            )
            transport.headers["Authorization"] = f"Bearer {new_access_token}"
            return client.execute(query, variable_values=variable_values)
        else:
            raise e


if __name__ == '__main__':
    # Get Bearer token
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")
    bearer_key = get_bearer_token(client_id=API_KEY, client_secret=API_SECRET)

    # Run request
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

    yesterday = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_iso = yesterday.isoformat().replace("+00:00", "Z")
    variable_values = {
        "postedAfter": yesterday_iso
    }
    query = gql("""
    query($postedAfter: DateTime) {
      posts(first: 2, postedAfter: $postedAfter, order:VOTES) {
        totalCount
        nodes {
          id
          url
          name
          tagline
          createdAt
          description
          commentsCount
          votesCount
        }
      }
    }
    """)

    response = execute_query(query, client, transport, variable_values=variable_values)
    total_count = response.get('posts', {}).get('totalCount', 0)
    posts = response.get('posts', {}).get('nodes', [])
    print(f"Total Posts: {total_count}")
    for post in posts:
        print(f"ID: {post['id']}")
        print(f"Name: {post['name']}")
        print(f"URL: {post['url']}")
        print(f"Tagline: {post['tagline']}")
        print(f"Description: {post['description']}")
        print(f"Comments: {post['commentsCount']}")
        print(f"Votes: {post['votesCount']}")
        print(f"Created at: {post['createdAt']}")
        print("-" * 30)
