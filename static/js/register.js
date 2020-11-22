const usernameAvailabilityUrl = 'check';

$(document).ready(() => {
    setupFormListeners();
});

function setupFormListeners() {
    $('.form-group input').on('keyup', (e) => listenFormField(e));
    $('form').on('submit', listenFormSubmit);
}

function listenFormField(e) {
    const target = e.target;
    if (target.id === 'username') {
        listenFormFieldLogin(target);
    } else {
        listenFormFieldRegular(target);
    }
}

function listenFormFieldRegular(target) {
    if (!isValid(target.id, target.value)) {
        const message = getInvalidMessage(target.id);
        addOrChangeInvalidFlag(target, message);
    } else {
        removeInvalidFlag(target);
    }
}

function listenFormFieldLogin(target) {
    if (target.value.length > 0) {
        $.get(usernameAvailabilityUrl, {username: target.value})
            .always((result, status) => {
                if (status !== 'success') {
                    addOrChangeInvalidFlag(target, 'Błąd połączenia z serwerem.');
                } else {
                    if (result[target.value] !== 'available' && result[target.value] !== undefined) {
                        addOrChangeInvalidFlag(target, 'Nazwa użytkownika zajęta.');
                    } else {
                        if (!isValid('username', target.value)) {
                            addOrChangeInvalidFlag(target, getInvalidMessage('username'));
                        } else {
                            removeInvalidFlag(target);
                        }
                    }
                }
            });
    } else {
        removeInvalidFlag(target);
    }
}

function removeInvalidFlag(target) {
    target.classList.remove('is-invalid');
        $(`.invalid-${target.id}`).remove();
        if (target.value.length > 0) {
            target.classList.add('is-valid');
        }
}

function addOrChangeInvalidFlag(target, msg) {
    if (!target.classList.contains('is-invalid')) {
            target.classList.add('is-invalid');
            $(target.parentElement).append(`<div class="invalid-feedback invalid-${target.id}">${msg}</div>`);
    } else {
        $('.invalid-' + target.id).text(msg);
    }
}

function listenFormSubmit(e) {
    if ($('.is-invalid').length > 0) {
        alert('Nie można wysłać formularza z powodu błędów!');
        return false;
    }
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
    } else if (fieldType === 'username') {
        return 'Długość nazwy użytkownika musi zawierać się w przedziale od 3 do 12 znaków.'
    } else {
        return 'Niewłaściwa wartość pola.'
    }
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
    } else if (fieldType === 'username') {
        return value.match(/[a-z]{3,12}/);
    } else if (fieldType === 'address') {
        return value.match(/.{5,}/);
    }else return false;
}
