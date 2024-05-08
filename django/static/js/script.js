// Fetches with X-Transcendence header
// inserts response HTML into target element
// returns response URL for history navigation
async function fetchData(
  url,
  { method, body } = { method: "GET", body: null }
) {
  const response = await fetch(url, {
    headers: {
      "X-Transcendence": true,
    },
    method,
    body,
  });

  const target_id = response.headers.get("X-Target-Id");
  const html = await response.text();

  document.getElementById(target_id).innerHTML = html;

  return response.url;
}

function handleFormSubmit(event) {
  event.preventDefault();

  const form = event.target;

  fetchData(form.action, {
    method: form.method,
    body: new FormData(form),
  })
    .then((response_url) => {
      // If the form returns a different URL, update the history
      if (response_url !== form.action) {
        history.pushState({ url: response_url }, null, response_url);
      }
    })
    .catch((error) => console.error(error));
}

// Navigation with history (forward and back buttons)
function handleNavigation(event) {
  const url = event.state ? event.state.url : window.location.href;

  fetchData(url).catch((error) => console.error(error));
}

window.addEventListener("popstate", handleNavigation);

// Navigation with links (anchor tags)
function handleLinkClick(event) {
  event.preventDefault();

  const url = event.target.href;

  fetchData(url)
    .then((response_url) => {
      history.pushState({ url: response_url }, null, response_url);
    })
    .catch((error) => console.error(error));
}

document.addEventListener("click", (event) => {
  if (event.target.tagName === "A") {
    handleLinkClick(event);
  }
});
