from typing import Any, Dict
import requests
import os
from secrets import DATABASE_INTERFACE_BEARER_TOKEN, HOST
from secrets import SOURCE, SOURCE_ID
SEARCH_TOP_K = 3


def upsert_file(directory: str):
    """
    Upload all files under a directory to the vector database.
    """
    url = HOST + "/upsert-file"
    headers = {"Authorization": "Bearer " + DATABASE_INTERFACE_BEARER_TOKEN}
    files = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            file_path = os.path.join(directory, filename)
            with open(file_path, "rb") as f:
                file_content = f.read()
                files.append(("file", (filename, file_content, "text/plain")))
            response = requests.post(url,
                                     headers=headers,
                                     files=files,
                                     timeout=600)
            if response.status_code == 200:
                print(filename + " uploaded successfully.")
            else:
                print(
                    f"Error: {response.status_code} {response.content} for uploading "
                    + filename)


def upsert(id: str, content: str):
    """
    Upload one piece of text to the database.
    """
    url = HOST + "/upsert"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + DATABASE_INTERFACE_BEARER_TOKEN,
    }

    data = {
      "documents": [
        {
          "id": id,
          "text": content,
          "metadata": {
            "source": SOURCE,
            "source_id": SOURCE_ID,
            # "created_at": "string",
            "author": "neal"
          }
        }
      ]
    }
    response = requests.post(url, json=data, headers=headers, timeout=600)

    if response.status_code == 200:
        print("uploaded successfully.")
    else:
        print(f"Error: {response.status_code} {response.content}")


def query_database(query_prompt: str) -> Dict[str, Any]:
    """
    Query vector database to retrieve chunk with user's input question.
    """
    url = HOST + "/query"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {DATABASE_INTERFACE_BEARER_TOKEN}",
    }
    # data = {"queries": [{"query": query_prompt, "top_k": SEARCH_TOP_K}]}
    data = {
      "queries": [
        {
          "query": query_prompt,
          "filter": {
              "source": SOURCE
              # "source_id": "string",
              # "url": "string",
              # "created_at": "string",
              # "author": "string"
          },
          "top_k": SEARCH_TOP_K
        }
      ]
    }
    response = requests.post(url, json=data, headers=headers, timeout=600)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")

def generate_uuid(class_name: str, identifier: str,
                  test: str = 'teststrong') -> str:
    """ Generate a uuid based on an identifier

    :param identifier: characters used to generate the uuid
    :type identifier: str, required
    :param class_name: classname of the object to create a uuid for
    :type class_name: str, required
    """
    test = 'overwritten'
    import uuid
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, class_name + identifier))


if __name__ == "__main__":
    # upsert_file("<directory_to_the_sample_data>")
    # upsert_file("./")
    content = "You can use my sample data. This is a fantasy world story made up by GPT from scratch. But feel free you use your own sample data. You may take a look at my data and check the format. It is just a list of text files in natural languages."
    discord_uuid = generate_uuid('discord', content)
    # upsert(discord_uuid,content)
    # upsert("2","Good morning , the weather is very good")
    print(query_database("what is the weather"))