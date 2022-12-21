document.addEventListener('DOMContentLoaded', () => {
  // Handle new post form submission
  const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  const newPostForm = document.querySelector('#new-post-form');
  if (newPostForm) {
    newPostForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const text = newPostForm.querySelector('textarea').value;
      fetch('/new_post/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ text }),
      })
        .then((response) => response.json())
        .then((data) => {
          // Append the new post to the list of posts
          const postList = document.querySelector('#post-list');
          const newPost = createPostElement(data);
          postList.prepend(newPost);
        });
    });
  }

  const likeButtons = document.querySelectorAll('.like-btns');

  likeButtons.forEach((button) => {
    const postId = button.getAttribute('data-post-id');
    fetch(`/like_post/${postId}/`)
      .then((response) => response.json())
      .then((data) => {
        if (data.is_liked) {
          button.classList.add('active');
        }
        button.querySelector('.badge').innerText = data.like_count;
      });
    button.addEventListener('click', (event) => {
      event.preventDefault();
      //const postId = button.getAttribute('data-post-id');
      fetch(`/like_post/${postId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `csrfmiddlewaretoken=${csrfToken}`,
      })
        .then((response) => response.json())
        .then((data) => {
          button.classList.toggle('active');
          button.querySelector('.badge').innerText = data.like_count;
        });
    });
  });

  // Handle edit button clicks
  const editButtons = document.querySelectorAll('.edit-button');
  editButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      const postId = button.getAttribute('data-post-id');
      const postContent = document.querySelector(`#post-${postId} .card-text`);
      const textarea = document.createElement('textarea');
      textarea.value = postContent.innerText;
      postContent.innerHTML = '';
      postContent.appendChild(textarea);
      button.style.display = 'none';
      const saveButton = button.nextElementSibling;
      saveButton.style.display = 'inline';
    });
  });

  const saveButtons = document.querySelectorAll('.save-button');
  saveButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      const postId = button.getAttribute('data-post-id');
      const postContent = document.querySelector(
        `#post-${postId} .card-text textarea`
      );
      fetch(`/edit_post/${postId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ text: postContent.value }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Update the post content
            const postElement = document.querySelector(
              `#post-${postId} .card-text`
            );
            postElement.innerHTML = data.text;
            // Hide the textarea and show the save button
            postContent.style.display = 'none';
            button.style.display = 'none';
            const editButton = button.previousElementSibling;
            editButton.style.display = 'inline';
          } else {
            alert('Error');
            postContent.style.display = 'none';
            button.style.display = 'none';
            const editButton = button.previousElementSibling;
            editButton.style.display = 'inline';
          }
        });
    });
  });

  // Handle pagination links
  const paginationLinks = document.querySelectorAll('.pagination a');
  paginationLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      const page = link.dataset.page;
      fetch(`/all_posts/?page=${page}`)
        .then((response) => response.json())
        .then((data) => {
          const postList = document.querySelector('#post-list');
          postList.innerHTML = '';
          data.posts.forEach((postData) => {
            const post = createPostElement(postData);
            postList.appendChild(post);
          });
        });
    });
  });

  //profile follow unfollow
  const followButton = document.querySelector('.follow-btn');
  const unfollowButton = document.querySelector('.unfollow-btn');
  //console.log(followButton);
  //console.log(unfollowButton);
  if (followButton) {
    followButton.addEventListener('click', (event) => {
      event.preventDefault();
      const userId = followButton.getAttribute('data-user-id');
      fetch(`/follow/${userId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `csrfmiddlewaretoken=${csrfToken}`,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            followButton.style.display = 'none';
            //unfollowButton.style.display = 'inline-block';
            //refresh page
            location.reload();
          } else {
            alert('Error');
          }
        });
    });
  }

  //profile follow unfollow
  if (unfollowButton) {
    unfollowButton.addEventListener('click', (event) => {
      event.preventDefault();
      const userId = unfollowButton.getAttribute('data-user-id');
      fetch(`/unfollow/${userId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `csrfmiddlewaretoken=${csrfToken}`,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            //followButton.style.display = 'inline-block';
            location.reload();
            //unfollowButton.style.display = 'none';
          } else {
            alert('Error');
          }
        });
    });
  }
});

function createPostElement(data) {
  // Create a new post element based on the data
  const post = document.createElement('li');
  post.classList.add('list-group-item');
  post.innerHTML = `
          <div>
            <strong>${data.user}</strong>
            <span class="text-muted">${data.created_at}</span>
            <form class="edit-post-form" data-post-id="${data.id}" style="display: none;">
        <textarea class="form-control">${data.text}</textarea>
        <button type="submit" class="btn btn-primary mt-2">Save</button>
      </form>
    `;
  return post;
}
