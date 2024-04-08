function handleResponse(response) {
    target = response.headers.get('Target');
    if (target === null) {
        target = 'main';
    }

    response.text().then(htmlContent => {
        history.pushState(null, '', response.url);
        document.getElementById(target).innerHTML = htmlContent;
    });
}

function fetchHTML(url) {
    fetch(url, {
        headers: {
            'Transcendence': 'true',
        },
    })
    .then(response => handleResponse(response));
}

function fetchForm(event) {
    event.preventDefault();

    const form = event.target;

    fetch(form.action, {
        method: form.method,
        headers: {
            'Transcendence': 'true',
        },
        body: new FormData(form),
    })
    .then(response => handleResponse(response));
}
