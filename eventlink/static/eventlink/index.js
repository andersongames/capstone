// this function copies the value of the input field with the ID event_link to the clipboard
// Used in the profile page
function copyLink() {
    const copyText = document.getElementById("event_link");
    copyText.select();
    document.execCommand("copy");
    alert("Link copied to clipboard!");
}

// this function generates the event creation link based on the current URL and the user id
// I decided to use the current URL so that this works in different environments, e.g. local and codespaces
// Used in the profile page
function generateCreateEventLink(inputElem) {
    // get the current URL and the createURL value
    const createURL = inputElem.value;
    const currentURL = window.location.href;

    // define the segment to be replaced
    const segmentToReplace = '/profile/';

    // check if the current URL contains the segmentToReplace
    if (currentURL.includes(segmentToReplace)) {
        // replace the segment with the createURL value
        const newURL = currentURL.replace(segmentToReplace, createURL);

        // update the input field with the new URL
        inputElem.value = newURL;
    }
}

// this function is responsible for displaying a modal (dialog box), by changing its display properties
// depending on the modal ID, it updates the modal content with the provided data
// Used for modals that handle event acceptance, rejection, or cancellation
function openModal(modalId, eventName, organizerName, organizerEmail) {
    const modal = document.getElementById(modalId);
    const backdrop = modal.querySelector('.modal-backdrop');

    if (modal) {
        modal.style.display = 'block';
        modal.classList.add('show');
        backdrop.style.display = 'block';

        // set the event name and user details in the modal
        if (modalId.includes('acceptModal')) {
            document.getElementById('eventNameAccept' + modalId.replace('acceptModal', '')).textContent = eventName;
            document.getElementById('eventOrganizerAccept' + modalId.replace('acceptModal', '')).textContent = `${organizerName} (${organizerEmail})`;
        } else if (modalId.includes('rejectModal')) {
            document.getElementById('eventNameReject' + modalId.replace('rejectModal', '')).textContent = eventName;
            document.getElementById('eventOrganizerReject' + modalId.replace('rejectModal', '')).textContent = `${organizerName} (${organizerEmail})`;
        } else if (modalId.includes('cancelModal')) {
            document.getElementById('eventNameCancel' + modalId.replace('cancelModal', '')).textContent = eventName;
            document.getElementById('eventOrganizerCancel' + modalId.replace('cancelModal', '')).textContent = `${organizerName} (${organizerEmail})`;
        }
    }
}

// this function closes a modal by changing its display properties, given the modal ID
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    const backdrop = modal.querySelector('.modal-backdrop');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
        backdrop.style.display = 'none';
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // generate the create event link
    const inputElem = document.getElementById("event_link");
    if (inputElem) {
        generateCreateEventLink(inputElem);
    }

    // add listener to copy link button
    const copyButton = document.querySelector('.btn-copy-link');
    if (copyButton) {
        copyButton.addEventListener("click", copyLink);
    }

    // close modal when clicking outside of the modal content
    const anyModal = document.querySelector('.modal');
    if (anyModal) {
        document.addEventListener("click", function(event) {
            if (event.target.classList.contains('modal-backdrop')) {
                const modal = event.target.closest('.modal');
                if (modal) {
                    closeModal(modal.id);
                }
            }
        });
    }

    // toggle the show class on the navbar items when the hamburger menu button is clicked
    const toggler = document.querySelector('.navbar-toggler');
    const navbarNav = document.querySelector('#navbarNav');
    toggler.addEventListener("click", function() {
        navbarNav.classList.toggle('show');
    });
});
