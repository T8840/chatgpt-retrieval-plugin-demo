from typing import Any, Dict
import requests
import os
from secrets import DATABASE_INTERFACE_BEARER_TOKEN, HOST
from datetime import datetime
import json

SEARCH_TOP_K = 5

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def upsert_files(directory: str):
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

def upsert_file(filename: str, source: str="file", source_id: str=None, author: str=None):
    """
    Upload all files under a directory to the vector database.
    """
    url = HOST + "/upsert-file"
    headers = {"Authorization": "Bearer " + DATABASE_INTERFACE_BEARER_TOKEN}
    directory = "./uploads"
    files = []
    metadata =  {
            "source": source,
            "source_id": source_id,
            "created_at": current_time,
            "author": author
          }
    metadata_str = json.dumps(metadata)
    data = {"metadata": metadata_str}
    print(data)
    if os.path.isfile(os.path.join(directory, filename)):
        file_path = os.path.join(directory, filename)
        with open(file_path, "rb") as f:
            file_content = f.read()
            files.append(("file", (filename, file_content, "text/plain")))
        response = requests.post(url,
                                 headers=headers,
                                 files=files,
                                 data= data,
                                 timeout=600)
        if response.status_code == 200:
            print(filename + " uploaded successfully.")
            print(response.content)
        else:
            print(
                f"Error: {response.status_code} {response.content} for uploading "
                + filename)
    else:
        print(
            f"Error: Can't find the {filename} "
            )

def upsert(id: str, content: str, source: str="email", source_id: int=None, author: str=None):
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
            "source": source,
            "source_id": source_id,
            "created_at": current_time,
            "author": author
          }
        }
      ]
    }
    response = requests.post(url, json=data, headers=headers, timeout=600)

    if response.status_code == 200:
        print(f"{source_id} upsert successfully.")
    else:
        print(f"Error: {response.status_code} {response.content}")


def query_database(query_prompt: str, source: str = None, source_id : str = None, author: str=None, top_k: int = SEARCH_TOP_K) -> Dict[str, Any]:
    """
    Query vector database to retrieve chunk with user's input questions.
    """
    url = HOST + "/query"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {DATABASE_INTERFACE_BEARER_TOKEN}",
    }
    # data = {"queries": [{"query": query_prompt, "top_k": 5}]}
    data = {
        "queries": [
            {
                "query": query_prompt,
                "filter": {
                    "source": source,
                    "source_id": source_id,
                    "author": author
                },
                "top_k": top_k
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")

def delete_database(source: str = None, source_id : str = None, author: str=None, top_k: int = SEARCH_TOP_K) -> Dict[str, Any]:
    pass


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
    # upsert_files("<directory_to_the_sample_data>")
    # upsert_file("example.txt",source_id="9")
    print(query_database("question？"))
    # content = "You can use my sample data. This is a fantasy world story made up by GPT from scratch. But feel free you use your own sample data. You may take a look at my data and check the format. It is just a list of text files in natural languages."
    # discord_uuid = generate_uuid('discord', content)
    # upsert(discord_uuid,content,source="mail",source_id=9999)
    # upsert("2","Good morning , the weather is very good")
    # # print(query_database("my sample data is what",source="email",source_id=9999))
    # print(query_database("What is a vector database"))