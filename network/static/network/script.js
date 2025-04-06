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
  // EDIT BUTTON
  document.querySelectorAll(".edit-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const postId = button.dataset.postId;
      const card = button.closest(".card");
      const contentP = card.querySelector("p");
      const originalContent = contentP.textContent;

      // Replace content with textarea
      const textarea = document.createElement("textarea");
      textarea.className = "form-control";
      textarea.value = originalContent;

      // Create Save button
      const saveBtn = document.createElement("button");
      saveBtn.textContent = "Save";
      saveBtn.className = "btn btn-sm btn-info mt-2";

      // Replace paragraph with textarea
      contentP.replaceWith(textarea);
      button.replaceWith(saveBtn);

      // Save logic
      saveBtn.addEventListener("click", () => {
        fetch(`/posts/${postId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ content: textarea.value }),
        })
          .then((response) => response.json())
          .then((data) => {
            const newP = document.createElement("p");
            newP.textContent = textarea.value;
            textarea.replaceWith(newP);
            saveBtn.replaceWith(button);
          });
      });
    });
  });
});
