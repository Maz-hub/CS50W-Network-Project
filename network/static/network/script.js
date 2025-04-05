// CSRF token helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// LIKE BUTTON
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".like-icon").forEach((icon) => {
    icon.addEventListener("click", () => {
      const postId = icon.dataset.postId;
      const liked = icon.dataset.liked === "true";
      const span = icon.nextElementSibling;

      // Optimistically update UI
      icon.classList.toggle("liked");
      icon.dataset.liked = (!liked).toString();
      let currentLikes = parseInt(span.textContent);
      span.textContent = liked ? currentLikes - 1 : currentLikes + 1;

      // Send POST request to backend
      fetch(`/like/${postId}`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })
        .then((response) => response.json())
        .then((data) => {
          // Ensure UI reflects backend truth
          span.textContent = data.likes_count;
          icon.dataset.liked = data.liked;
          icon.classList.toggle("liked", data.liked);
        });
    });
  });
});
