window.onload = function() {
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to add a new post
function addPost() {
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;
    var postDate = document.getElementById('post-date').value;

    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: postTitle, content: postContent, author: postAuthor, date: postDate })
    })
    .then(response => response.json())
    .then(post => {
        console.log('Post added:', post);
        loadPosts();
    })
    .catch(error => console.error('Error:', error));
}

// Function to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    fetch(baseUrl + '/posts/' + postId, { method: 'DELETE' })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts();
    })
    .catch(error => console.error('Error:', error));
}

// Function to like a post
function likePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    fetch(baseUrl + '/posts/' + postId + '/like', { method: 'POST' })
    .then(response => response.json())
    .then(updatedPost => {
        document.getElementById(`like-count-${postId}`).innerText = updatedPost.likes;
    })
    .catch(error => console.error('Error:', error));
}

// Function to search posts
function searchPosts() {
    var baseUrl = document.getElementById('api-base-url').value;
    var title = document.getElementById('search-title').value;
    var content = document.getElementById('search-content').value;
    var author = document.getElementById('search-author').value;
    var date = document.getElementById('search-date').value;

    let searchParams = [];
    if (title) searchParams.push(`title=${title}`);
    if (content) searchParams.push(`content=${content}`);
    if (author) searchParams.push(`author=${author}`);
    if (date) searchParams.push(`date=${date}`);

    let url = baseUrl + '/posts/search';
    if (searchParams.length > 0) {
        url += '?' + searchParams.join('&');
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                postDiv.innerHTML = `
                    <h2>${post.title}</h2>
                    <p>${post.content}</p>
                    <p><strong>Author:</strong> ${post.author}</p>
                    <p><small>${post.date}</small></p>
                    <div class="post-footer">
                        <button class="like-button" onclick="likePost(${post.id})">
                            ❤️ <span id="like-count-${post.id}">${post.likes}</span>
                        </button>
                        <button class="delete-button" onclick="deletePost(${post.id})">Delete</button>
                    </div>
                `;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Function to sort posts
function sortPosts() {
    var sortBy = document.getElementById('sort-by').value;
    var direction = document.getElementById('sort-direction').value;
    loadPosts(sortBy, direction);
}

// Function to edit and show update option with pre-filled data
function editPost(postId) {
    const postDiv = document.getElementById(`post-${postId}`);
    const title = postDiv.querySelector('.post-title');
    const content = postDiv.querySelector('.post-content');
    const author = postDiv.querySelector('.post-author');
    const date = postDiv.querySelector('.post-date');

    // Hide the original post content and show editable fields
    title.style.display = 'none';
    content.style.display = 'none';
    author.style.display = 'none';
    date.style.display = 'none';

    // Show the input fields and update button
    const titleInput = postDiv.querySelector('.edit-title');
    const contentInput = postDiv.querySelector('.edit-content');
    const authorInput = postDiv.querySelector('.edit-author');
    const dateInput = postDiv.querySelector('.edit-date');
    const updateButton = postDiv.querySelector('.update-button');
    const editButton = postDiv.querySelector('.edit-button');

    // Populate fields with current data
    titleInput.value = title.innerText;
    contentInput.value = content.innerText;
    authorInput.value = author.innerText.replace("Author:", "").trim();
    dateInput.value = date.innerText.replace("Date:", "").trim();

    titleInput.style.display = 'block';
    contentInput.style.display = 'block';
    authorInput.style.display = 'block';
    dateInput.style.display = 'block';
    updateButton.style.display = 'block';
    editButton.style.display = 'none';  // Hide the edit button
}

// Function to display posts with editable fields
function loadPosts(sortBy = '', direction = '') {
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    let url = baseUrl + '/posts';
    if (sortBy) {
        url += `?sort=${sortBy}&direction=${direction}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                postDiv.id = `post-${post.id}`;
                postDiv.innerHTML = `
                    <h2 class="post-title">${post.title}</h2>
                    <p class="post-content">${post.content}</p>
                    <p class="post-author"><strong>Author:</strong> ${post.author}</p>
                    <p class="post-date"><strong>Date:</strong> ${post.date}</p>
                    <div class="post-footer">
                        <button class="like-button" onclick="likePost(${post.id})">❤️ <span id="like-count-${post.id}">${post.likes}</span></button>
                        <button class="delete-button" onclick="deletePost(${post.id})">Delete</button>
                        <button class="edit-button" onclick="editPost(${post.id})">Edit</button>
                        <button class="update-button" style="display:none" onclick="updatePost(${post.id})">Update Comment</button>
                    </div>

                    <!-- Hidden editable fields -->
                    <input class="edit-title" type="text" style="display:none">
                    <textarea class="edit-content" style="display:none"></textarea>
                    <input class="edit-author" type="text" style="display:none">
                    <input class="edit-date" type="text" style="display:none">
                `;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));
}

function isValidDate(dateString) {
    // Regular expression for YYYY-MM-DD format
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    return dateString.match(regex) && !isNaN(new Date(dateString).getTime());
}

// Function to update a post with date validation
function updatePost(postId) {
    const postDiv = document.getElementById(`post-${postId}`);
    const title = postDiv.querySelector('.edit-title').value;
    const content = postDiv.querySelector('.edit-content').value;
    const author = postDiv.querySelector('.edit-author').value;
    const date = postDiv.querySelector('.edit-date').value;

    // Validate the date format
    if (!isValidDate(date)) {
        alert("Please enter a valid date in the format YYYY-MM-DD.");
        return;  // Prevent update if the date is invalid
    }

    var baseUrl = document.getElementById('api-base-url').value;

    // Send the update request to the server
    fetch(baseUrl + '/posts/' + postId, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, author, date })
    })
    .then(response => response.json())
    .then(updatedPost => {
        console.log('Post updated:', updatedPost);
        loadPosts();  // Reload posts after update
    })
    .catch(error => console.error('Error:', error));
}
