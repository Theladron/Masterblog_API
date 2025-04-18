import json
import os
from json import JSONDecodeError

STORAGE_PATH = f"""{os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                                 'data', 'storage.json'))}"""


def save_file(new_data):
    """
    Saves the provided data to the storage file after checking its integrity.
    :param new_data: The list of comments to be saved in the file
    """
    required_keys = ["id", "title", "content", "author", "date", "likes"]
    if not all(isinstance(comment, dict)
               and all(key in comment for key in required_keys) for comment in new_data):
        print("Error. File is corrupted. Save aborted.")
        return

    with open(STORAGE_PATH, "w", encoding="utf-8") as handle:
        json.dump(new_data, handle, indent=4)


def list_comments():
    """
    Retrieves the list of comments from the storage file, handles exceptions
    :return: List of comments if the file is valid, else an empty list
    """
    try:
        with open(STORAGE_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, JSONDecodeError):
        with open(STORAGE_PATH, "w", encoding="utf-8") as handle:
            json.dump([], handle, indent=4)
        return []
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        with open(STORAGE_PATH, "w", encoding="utf-8") as handle:
            json.dump([], handle, indent=4)
        return []


def add_comment(comment):
    """
    Adds a new comment to the list and saves it in the storage file after checking its integrity.
    :param comment: The comment dictionary to be added to the list
    :return: The added comment if successful, else None
    """
    if not all(comment.get(key) for key in ["title", "content", "author", "date"]):
        return None

    data = list_comments()
    data.append(comment)
    save_file(data)
    return comment


def delete_comment(comment_id):
    """
    Deletes a comment identified by its ID from the list and saves the updated list
    if the id is present in the database
    :param comment_id: The ID of the comment to be deleted.
    :return: The ID of the deleted comment if successful, else None
    """
    data = list_comments()
    comment = next((c for c in data if c.get("id") == comment_id), None)
    if not comment:
        return None

    data.remove(comment)
    save_file(data)
    return comment_id


def update_comment(index, comment):
    """
    Updates a comment at the specified index with new data and saves the updated list
    after checking its integrity.
    :param index: The index of the comment to be updated.
    :param comment: The new comment data.
    :return: The updated comment if successful, else None
    """
    data = list_comments()

    if index >= len(data):
        return None

    if not all(comment.get(key) for key in ["title", "content", "author", "date"]):
        return None

    data[index] = comment
    save_file(data)
    return comment
