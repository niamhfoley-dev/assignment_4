async function toggleReaction(postId, reactionType) {
    const likeCountElem = document.getElementById(`like-count-${postId}`);
    const dislikeCountElem = document.getElementById(`dislike-count-${postId}`);

    try {
        const response = await fetch(`/posts/post/${postId}/${reactionType}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
        });

        if (response.ok) {
            const data = await response.json();

            // Update counts dynamically
            likeCountElem.textContent = data.likes;
            dislikeCountElem.textContent = data.dislikes;
        } else {
            alert('Failed to update reaction. Please try again.');
        }
    } catch (error) {
        console.error('Error toggling reaction:', error);
        alert('An error occurred. Please try again later.');
    }
}