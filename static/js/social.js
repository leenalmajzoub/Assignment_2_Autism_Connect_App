function commentReplyToggle(parent_id) {
	const row = document.getElementById(parent_id);

	if (row.classList.contains('d-none')) {
		row.classList.remove('d-none');
	} else {
		row.classList.add('d-none');
	}
}

function shareToggle(parent_id) {
	const row = document.getElementById(parent_id);

	if (row.classList.contains('d-none')) {
		row.classList.remove('d-none');
	} else {
		row.classList.add('d-none');
	}
}

function shareEvent(eventId) {
    console.log(`Clicked on event ID: ${eventId}`);
    const form = document.getElementById(eventId);
    
    if (form.classList.contains('d-none')) {
        form.classList.remove('d-none');
    } else {
        form.classList.add('d-none');
    }
}


function showNotifications() {
	const container = document.getElementById('notification-container');

	if (container.classList.contains('d-none')) {
		container.classList.remove('d-none');
	} else {
		container.classList.add('d-none');
	}
}


function showNotifications() {
	const container = document.getElementById('notification-container');

	if (container.classList.contains('d-none')) {
		container.classList.remove('d-none');
	} else {
		container.classList.add('d-none');
	}
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function removeNotification(removeNotificationURL, redirectURL) {
	const csrftoken = getCookie('csrftoken');
	let xmlhttp = new XMLHttpRequest();

	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == XMLHttpRequest.DONE) {
			if (xmlhttp.status == 200) {
				window.location.replace(redirectURL);
			} else {
				alert('There was an error');
			}
		}
	};

	xmlhttp.open("DELETE", removeNotificationURL, true);
	xmlhttp.setRequestHeader("X-CSRFToken", csrftoken);
	xmlhttp.send();
}

function formatTags() {
	const elements = document.getElementsByClassName('body');
	for (let i = 0; i < elements.length; i++) {
		let bodyText = elements[i].children[0].innerText;

		let words = bodyText.split(' ');

		for (let j = 0; j < words.length; j++) {
			if (words[j][0] === '#') {
				let replacedText = bodyText.replace(/\s\#(.*?)(\s|$)/g, ` <a href="/social/explore?query=${words[j].substring(1)}">${words[j]}</a>`);
				elements[i].innerHTML = replacedText;
			}
		}
	}
}

document.addEventListener("DOMContentLoaded", function() {
    // Get the URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const activeForm = urlParams.get('active_form');

    // Set the default form to be shown if none is specified
    let defaultForm = 'post';

    // If an active form is specified, use it; otherwise, use the default
    if (activeForm) {
        defaultForm = activeForm;
    }

    // Show the specified form
    document.getElementById(defaultForm).classList.add('show');

    // Add an event listener to each button to handle the click event
    document.querySelectorAll('button[data-bs-toggle="collapse"]').forEach(button => {
        button.addEventListener('click', function(event) {
            // Hide all collapsible sections
            document.querySelectorAll('.collapse').forEach(section => {
                section.classList.remove('show');
            });

            // Show the clicked section
            const target = this.getAttribute('data-bs-target').substring(1);
            document.getElementById(target).classList.add('show');
        });
    });
});



formatTags();