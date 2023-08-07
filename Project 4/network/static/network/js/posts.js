window.addEventListener("DOMContentLoaded", (event) => {
  // Add event listener to new posting area
  let content = document.querySelector('#post-body');
  if (content != null) {
    content.addEventListener('keyup',() => button_status(content, document.querySelector('#post-btn')));
  }
  // Add event listener to all edit buttons
  let posts = document.querySelectorAll('.post');
  posts.forEach((post) => {
    let btn = post.querySelector('#edit-btn');
    if (btn != null) {
      post.querySelector('#edit-btn').addEventListener('click', () => editPost(post));
      post.querySelector('#cancel-btn').addEventListener('click', () => cancelEdit(post, post.querySelector('#content-area').innerText));
      post.querySelector('#save-btn').addEventListener('click', () => saveEdit(post));
      post.querySelector('#edit-area').addEventListener('keyup', () => button_status(
        post.querySelector('#edit-area'), post.querySelector('#save-btn')))
    }
  });

  // Add event listener to 'like' buttons
  let buttons = document.querySelectorAll("#like-button");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => change_like(btn));
  });
});

function button_status(content, btn) {
  if (content.value == "" || !content.value.replace(/\s/g, '').length) {
    btn.disabled = true;
  }
  else {
    btn.disabled = false;
  }
}

function editPost(post) {
  let current_text = post.querySelector('#content-area')

  let text_area = post.querySelector('#edit-area');
  text_area.value = current_text.innerText;

  changeElementVisibility(
    [post.querySelector('#edit-btn'),
    post.querySelector('#save-btn'),
    post.querySelector('#cancel-btn'),
    text_area,
    current_text]
  );
}

function saveEdit(post) {
 let content = post.querySelector('#content-area');
 let text_area = post.querySelector('#edit-area')
 let id = post.getAttribute('data-id');

  fetch("/save_edit/" + id, {
    method: 'POST',
    body: JSON.stringify({
      content: text_area.value
    })
  })
  .then(function(response) {
    if (response.ok) {
      return response.json()
    }
    else {
      return Promise.reject('Error.')
    }
  })
  .then(function(data) {
    changeElementVisibility(
      [post.querySelector('#edit-btn'),
      post.querySelector('#save-btn'),
      post.querySelector('#cancel-btn'),
      text_area,
      content]
    );

    content.innerText = data.content;
  })
}

function cancelEdit(post, text) {

  let current_text = post.querySelector('#content-area');
  current_text.innerText = text;

  changeElementVisibility(
    [post.querySelector('#edit-btn'),
    post.querySelector('#save-btn'),
    post.querySelector('#cancel-btn'),
    post.querySelector('#edit-area'),
    current_text]
  );
}

function changeElementVisibility(elements) {
  elements.forEach((element) => {
    element.hidden = !element.hidden;
  });
}

function change_like(btn) {
  let id = btn.getAttribute('data-id');
  fetch("/like/" + id, {
    method: 'POST'
  })
  .then(function(response) {
    if (response.ok) {
      return response.json()
    }
    else {
      return Promise.reject('Error.')
    }
  })
  .then(function(data) {
    btn.src = data.is_liked ? '/static/network/liked.png' : '/static/network/unliked.png';
    document.querySelector("#likes-count-" + id).innerText = data.likes;
  });
}

