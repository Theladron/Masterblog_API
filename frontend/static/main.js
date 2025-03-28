window.onload = function() {
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to fetch all posts from the API and display them
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
