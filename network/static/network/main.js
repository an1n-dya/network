document.addEventListener('DOMContentLoaded', function() {

    // Use event delegation for all click events
    document.body.addEventListener('click', function(event) {

        const target = event.target;

        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        if (!csrftoken) {
            console.error('CSRF token not found');
            return;
        }

        // Edit button clicked
        if (target.matches('.edit-btn')) {
            const postId = target.dataset.postId;
            document.getElementById(`post-content-${postId}`).style.display = 'none';
            document.getElementById(`post-edit-${postId}`).style.display = 'block';
            target.style.display = 'none';
        }

        // Cancel button clicked
        if (target.matches('.cancel-btn')) {
            const postId = target.dataset.postId;
            document.getElementById(`post-content-${postId}`).style.display = 'block';
            document.getElementById(`post-edit-${postId}`).style.display = 'none';
            document.querySelector(`.edit-btn[data-post-id="${postId}"]`).style.display = 'inline-block';
        }

        // Save button clicked
        if (target.matches('.save-btn')) {
            const postId = target.dataset.postId;
            const content = document.getElementById(`edit-content-${postId}`).value.trim();
            const saveBtn = target;

            if (!content) {
                alert('Content cannot be empty');
                return;
            }

            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';

            fetch(`/edit_post/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ content: content })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`post-content-${postId}`).textContent = data.content;
                    document.getElementById(`post-content-${postId}`).style.display = 'block';
                    document.getElementById(`post-edit-${postId}`).style.display = 'none';
                    
                    const editBtn = document.querySelector(`.edit-btn[data-post-id="${postId}"]`);
                    editBtn.style.display = 'inline-block';
                    
                    const originalButtonText = 'Edit';
                    editBtn.textContent = 'Saved!';
                    editBtn.classList.remove('btn-outline-secondary');
                    editBtn.classList.add('btn-success');

                    setTimeout(() => {
                        editBtn.textContent = originalButtonText;
                        editBtn.classList.remove('btn-success');
                        editBtn.classList.add('btn-outline-secondary');
                    }, 2000);

                } else {
                    alert(data.error || 'Error updating post');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while saving.');
            })
            .finally(() => {
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save';
            });
        }

        // Like button clicked (check for closest button)
        const likeBtn = target.closest('.like-btn');
        if (likeBtn) {
            const postId = likeBtn.dataset.postId;
            fetch(`/toggle_like/${postId}`, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken }
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_liked) {
                    likeBtn.classList.add('btn-danger');
                    likeBtn.classList.remove('btn-outline-danger');
                } else {
                    likeBtn.classList.add('btn-outline-danger');
                    likeBtn.classList.remove('btn-danger');
                }
                likeBtn.querySelector('.like-count').textContent = data.like_count;
            })
            .catch(error => console.error('Error:', error));
        }

        // Follow button clicked
        if (target.matches('.follow-btn')) {
            const username = target.dataset.username;
            fetch(`/toggle_follow/${username}`, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken }
            })
            .then(response => response.json())
            .then(data => {
                const followText = target.querySelector('.follow-text');
                if (data.is_following) {
                    target.classList.add('btn-outline-primary');
                    target.classList.remove('btn-primary');
                    if(followText) followText.textContent = 'Unfollow';
                } else {
                    target.classList.add('btn-primary');
                    target.classList.remove('btn-outline-primary');
                    if(followText) followText.textContent = 'Follow';
                }
                const followerCountEl = document.querySelector('.follower-count-value');
                if (followerCountEl) {
                    followerCountEl.textContent = data.follower_count;
                }
            })
            .catch(error => console.error('Error:', error));
        }
    });

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});