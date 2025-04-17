import os
import sys
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage.storage_json import (
    update_comment,
    delete_comment,
    add_comment,
    list_comments, save_file)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

SWAGGER_URL = "/api/docs"
API_URL_PATH = f"/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL_PATH,
    config={
        'app_name': 'Masterschool blog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/static/swagger.json')
def serve_swagger():
    """
    Serves the Swagger JSON file from the static directory.
    """
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'),
                               'masterschoolblog.json')


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    """
    Handles both GET and POST requests for the '/api/posts' endpoint
    - GET: Returns a list of all posts, optionally sorted by specified field and direction
    - POST: Creates a new post, validates the input data, and returns the newly created post
    :return: JSON response with posts or an error message
    """
    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is missing or invalid.'}), 400

        # checking for missing keys
        required_keys = ['title', 'content', 'author', 'date']
        if not all(data.get(key) for key in required_keys):
            missing_keys = [key for key in required_keys if not data.get(key)]
            return jsonify({'error': f"{', '.join(missing_keys)} are necessary."}), 400

        # checking for correct date format
        if not check_date_format(data):
            return jsonify({'error': 'Date format is invalid. Please use format "y-m-d"'}), 400

        unique_id = find_unique_id()
        new_post = {"id": unique_id,
                    "title": data['title'],
                    "content": data['content'],
                    "author": data['author'],
                    "date": data['date'],
                    "likes": 0}
        new_post = add_comment(new_post)
        return jsonify(new_post), 201

    posts = list_comments()
    if not posts:
        return jsonify({"error": "Data is empty. Please add a comment first"}), 404

    sort = request.args.get('sort', None)
    direction = request.args.get('direction', None)

    if sort or direction:
        if sort not in {"title", "content", "author", "date"}:
            return jsonify({"error": f"wrong input for sort: {sort}."}), 400

        if direction not in {"asc", "desc"}:
            return jsonify({"error": f"wrong input for direction: {direction}."}), 400

        posts = sort_posts(posts, sort, direction)

    return jsonify(posts)


@app.route('/api/posts/<id>', methods=['DELETE'])
def delete(id):
    """
    Deletes a post by its ID from the list of posts.
    :param id: The ID of the post to delete.
    :return: JSON response with a success message or an error message.
    """
    if not id.isdigit():
        return jsonify({'error': 'id must be an integer.'}), 400

    posts = list_comments()
    if not get_post_by_id(posts, id):
        return jsonify({'error': 'post not found.'}), 404

    deleted_id = delete_comment(int(id))
    return jsonify({'message': f"Post with id {deleted_id} has been deleted successfully."}), 200


@app.route('/api/posts/<id>', methods=['PUT'])
def update(id):
    """
    Updates an existing post identified by its ID.
    :param id: The ID of the post to update.
    :return: JSON response with the updated post or an error message if the post is not found or the data is incomplete.
    """
    posts = list_comments()

    if not posts:
        return jsonify({"error": "Data is empty. Please add a comment first"}), 404

    if not id.isdigit():
        return jsonify({'error': 'id must be an integer.'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON body.'}), 400

    post_to_update = get_post_by_id(posts, id)
    if not post_to_update:
        return jsonify({'error': f'id {id} does not exist.'}), 404

    valid_keys = ['title', 'content', 'author', 'date']
    has_valid = any(data.get(key) for key in valid_keys)
    if not has_valid:
        return jsonify({'error': 'At least one valid field must be provided.'}), 400

    for key in valid_keys:
        if data.get(key):
            if key == "date" and not check_date_format(data):
                return jsonify({"error": "Date format is invalid. Please use format 'y-m-d'"}), 400
            post_to_update[key] = data[key]

    index = posts.index(post_to_update)
    updated_post = update_comment(index, post_to_update)
    return jsonify(updated_post)


@app.route('/api/posts/search', methods=['GET'])
def search():
    """
    Searches for posts based on title, content, author, or date parameters.
    :return: JSON response with a list of posts that match the search criteria.
    """
    posts = list_comments()

    if not posts:
        return jsonify({"error": "Data is empty. Please add a comment first"}), 404

    title = request.args.get('title', None)
    content = request.args.get('content', None)
    author = request.args.get('author', None)
    date = request.args.get('date', None)

    if all(var is None for var in [title, content, author, date]):
        return jsonify(posts)
    result = [entry for entry in posts
              if (title and title.lower() in entry['title'].lower())
              or (content and content.lower() in entry['content'].lower())
              or (author and author.lower() in entry['author'].lower())
              or (date and date.lower() in entry['date'].lower())]

    return jsonify(result)


@app.route("/api/posts/<post_id>/like", methods=["POST"])
def like_post(post_id):
    """
    Increments the like count for a specific post
    :param post_id: ID of the post to be liked as integer
    :return: JSON response with the updated post, else an error message
    """
    posts = list_comments()

    if not posts:
        return jsonify({"error": "Data is empty. Please add a comment first"}), 404

    if not post_id.isdigit():
        return jsonify({'error': 'id must be an integer.'}), 400

    post = get_post_by_id(posts, post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    post["likes"] += 1
    save_file(posts)
    return jsonify(post), 200


def get_post_by_id(posts, id):
    """
    Helper function to find a post by its ID.
    :param posts: List of all posts
    :param id: ID of the post to find
    :return: Post if found, or None if not found
    """
    if not str(id).isdigit():
        return None
    return next((post for post in posts if post["id"] == int(id)), None)


def sort_posts(posts, sort_field, direction):
    """Sorts posts based on a given field and direction.
    :return: A list of sorted posts."""
    posts_copy = posts.copy()
    if sort_field == "date":
        try:
            posts_copy = [
                {**post, "date": datetime.strptime(post["date"], "%Y-%m-%d")}
                for post in posts_copy
            ]
        except ValueError:
            return posts  # if date parsing fails, return unsorted list
    return sorted(posts_copy, key=lambda x: x[sort_field], reverse=(direction == "desc"))


def find_unique_id():
    """
    Finds the next available unique ID for a new post.
    :return: A unique ID that is not already in use.
    """
    posts = list_comments()
    id_list = [int(entry['id']) for entry in posts if 'id' in entry and str(entry['id']).isdigit()]
    return next((int(num) for num in range(1, len(posts) + 2) if int(num) not in id_list))


def check_date_format(data):
    """
    Checks if the 'date' field in the provided data is in the correct format ("Y-m-d").
    :param data: The dictionary containing the 'date' field to check.
    :return: A datetime object if the date is valid, or "invalid" if the date is not valid.
    """
    date_str = data.get('date')
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None
    return None


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
