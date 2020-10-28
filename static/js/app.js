const loginAvailabilityUrl = 'https://infinite-hamlet-29399.herokuapp.com/check/';

$(document).ready(() => {
    setupFormListeners();
    loadJoke();
    showMessage();
    showShipmentInfo();
});

function setupFormListeners() {
    $('.form-group input').on('keyup', (e) => listenFormField(e));
    $('form').on('submit', listenFormSubmit);
}

function listenFormField(e) {
    const target = e.target;
    if (!isValid(target.id, target.value)) {
        const message = getInvalidMessage(target.id);
        if (!target.classList.contains('is-invalid')) {
            target.classList.add('is-invalid');
            $(target.parentElement).append(`<div class="invalid-feedback invalid-${target.id}">${message}</div>`);
        } else if (target.id === 'login') {
            $('.invalid-'+target.id).text(message);
        }
    } else {
        if (target.id === 'login') {
            $.get(loginAvailabilityUrl + target.value, (result, status) => {
                if (status === 'success') {
                    if (result[target.value] !== 'available') {
                        if (target.classList.contains('is-invalid')) {
                            $('.invalid-'+target.id).text('Nazwa użytkownika jest już zajęta.');
                        } else {
                            target.classList.add('is-invalid');
                            $(target.parentElement).append(`<div class="invalid-feedback invalid-${target.id}">Nazwa użytkownika jest już zajęta.</div>`);
                        }
                    } else {
                        removeInvalidFlag(target);
                    }
                } else {
                    target.classList.add('is-invalid');
                    $(target.parentElement).append(`<div class="invalid-feedback invalid-${target.id}">Błąd polączenia z serwerem.</div>`);
                }
            });
        }
        else {
            removeInvalidFlag(target);
        }
    }
}

function removeInvalidFlag(target) {
    target.classList.remove('is-invalid');
        $(`.invalid-${target.id}`).remove();
        if (target.value.length > 0) {
            target.classList.add('is-valid');
        }
}

function listenFormSubmit(e) {
    if ($('.is-invalid').length > 0) {
        alert('Nie można wysłać formularza z powodu błędów!');
        return false;
    }
}

function loadJoke() {
    $.get('https://sv443.net/jokeapi/v2/joke/Programming?blacklistFlags=nsfw,religious,political,racist,sexist&type=single',
        (result) => {
            $('.joke-container').append(`<h5 id="joke-content">${result.joke}</h5>`);
            $('#joke-content').fadeIn(2000);
        }
    )
}

function isValid(fieldType, value) {
    const plUppercase = 'ĄĆĘŁŃÓŚŹŻ';
    const plLowercase = 'ąćęłńóśźż';
    if (fieldType === 'firstname' || fieldType === 'lastname') {
        return value.match(new RegExp(`[A-Z${plUppercase}][a-z${plLowercase}]+`));
    } else if (fieldType === 'password') {
        return value.trim().match(/.{8,}/);
    } else if (fieldType === 'password_repeat') {
        return value === $('#password').val();
    } else if (fieldType === 'login') {
        return value.match(/[a-z]{3,12}/);
    } else if (fieldType === 'sex') {
        return ['M', 'F'].includes(value);
    } else if (fieldType === 'photo') {
        return fieldType !== null && fieldType !== undefined
    } else return false;
}

function getInvalidMessage(fieldType) {
    if (fieldType === 'firstname') {
        return 'Imię powinno zaczynać się dużą literą.';
    } else if (fieldType === 'lastname') {
        return 'Nazwisko powinno zaczynać się dużą literą.';
    } else if (fieldType === 'password') {
        return 'Hasło musi zawierać co najmniej 8 znaków.';
    } else if (fieldType === 'password_repeat') {
        return 'Hasła muszą być takie same.';
    } else if (fieldType === 'login') {
        return 'Długość nazwy użytkownika musi zawierać się w przedziale od 3 do 12 znaków.'
    } else {
        return 'Niewłaściwa wartość pola.'
    }
}

function showMessage() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    if (urlParams.has('msg-content') && urlParams.has('email')) {
        const msg = urlParams.get('msg-content');
        const email = urlParams.get('email');
        showAlert(`Wysłano wiadomość z adresu ${email}:`, msg, 'success');
    }
}

function showShipmentInfo() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    if (urlParams.has('shipment_number')) {
        const shipmentNumber = urlParams.get('shipment_number');
        showAlert(`Status paczki o numerze: ${shipmentNumber}:`, 'Nie znaleziono.', 'danger');
    }
}

function showAlert(header, content, alertStatus) {
    const messageContainer = document.createElement('div');
        messageContainer.className = "alert alert-" + alertStatus;
        const messageHeader = document.createElement('b');
        messageHeader.innerText = header;
        const messageContent = document.createElement('div');
        messageContent.innerText = content;
        messageContainer.appendChild(messageHeader);
        messageContainer.appendChild(messageContent);
        $('.container-fluid').append(messageContainer);
        $(messageContainer).fadeOut(4000);
}
