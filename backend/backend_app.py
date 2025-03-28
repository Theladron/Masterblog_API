from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from storage.storage_json import (
    update_comment,
    delete_comment,
    add_comment,
    list_comments, save_file)

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

SWAGGER_URL = "/api/docs"
API_URL_PATH = "/static/masterschoolblog.json"
API_URL = API_URL_PATH

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterschool blog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


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
        date = check_date_format(data)
        if date == "invalid":
            return jsonify({'error': 'Date format is invalid. please use format "y-m-d"'}), 400
        if not data or not all(
                key in data and data[key] for key in ['title', 'content', 'author', 'date']):
            missing_keys = [key for key in ['title', 'content', 'author', 'date']
                            if key not in data or not data[key]]
            return jsonify({'error': f"{', '.join(missing_keys)} are necessary."}), 400
        unique_id = find_unique_id()
        new_post = {"id": unique_id,
                    "title": data['title'],
                    "content": data['content'],
                    "author": data['author'],
                    "date": data['date'],
                    "likes": 0}
        new_post = add_comment(new_post)
        return jsonify(new_post), 201

    else:
        posts = list_comments()
        if not posts:
            return jsonify({"error": "Data is empty. Please add a comment first"}), 404
        sort = request.args.get('sort', None)
        direction = request.args.get('direction', None)
        if sort or direction:
            if sort not in {"title", "content", "author", "date"}:
                return jsonify({"error": f"wrong input for sort: {sort}."}), 400

            if direction not in {"ascending", "descending"}:
                return jsonify({"error": f"wrong input for direction: {direction}."}), 400

            # create a new dict with datetime-objects instead of strings if sorted by date
            if sort in "date":
                datetime_posts = [
                    {**post, "date": datetime.strptime(post["date"], "%Y-%m-%d")}
                    for post in posts
                ]
                new_posts = sorted(datetime_posts, key=lambda x: x[sort],
                                   reverse=(direction == "descending"))

            else:
                new_posts = sorted(posts, key=lambda x: x[sort],
                                   reverse=(direction == "descending"))
            return jsonify(new_posts)
        return jsonify(posts)


@app.route('/api/posts/<id>', methods=['DELETE'])
def delete(id):
    """
    Deletes a post by its ID from the list of posts.
    :param id: The ID of the post to delete.
    :return: JSON response with a success message or an error message.
    """
    if id.isdigit():
        id = delete_comment(int(id))
        if id:
            return jsonify({'message': f"Post with id {id} has been deleted successfully."}), 200

    return jsonify({'error': 'post not found.'}), 404


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
    data = request.get_json()
    for index, entry in enumerate(posts):
        if int(id) == entry["id"]:
            if data and any(data.get(key) for key in
                            ["title", "content", "author", "date"]):
                for key in ["title", "content", "author", "date"]:
                    if data.get(key):
                        entry[key] = data[key]
                updated_post = update_comment(index, entry)
                if updated_post:
                    return jsonify(updated_post)
            return jsonify({'error': 'data missing.'}), 404
    return jsonify({'error': f'id {id} does not exist.'}), 404


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


@app.route("/api/posts/<int:post_id>/like", methods=["POST"])
def like_post(post_id):
    """
    Increments the like count for a specific post
    :param post_id: ID of the post to be liked as integer
    :return: JSON response with the updated post, else an error message
    """
    posts = list_comments()  # Get the full list of posts
    for index, post in enumerate(posts):
        if post["id"] == post_id:
            posts[index]["likes"] += 1  # Modify the original list at the index
            save_file(posts)  # Save the ENTIRE list to persist changes
            return jsonify(posts[index]), 200  # Return the updated post

    return jsonify({"error": "Post not found"}), 404


def find_unique_id():
    """
    Finds the next available unique ID for a new post.
    :return: A unique ID that is not already in use.
    """
    posts = list_comments()
    id_list = [int(entry['id']) for entry in posts]
    return next((int(num) for num in range(1, len(posts) + 2) if int(num) not in id_list))


def check_date_format(data):
    """
    Checks if the 'date' field in the provided data is in the correct format ("Y-m-d").
    :param data: The dictionary containing the 'date' field to check.
    :return: A datetime object if the date is valid, or "invalid" if the date is not valid.
    """
    try:
        date = datetime.strptime(data['date'], format("%Y-%m-%d"))
    except ValueError:
        return "invalid"
    else:
        return date


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
