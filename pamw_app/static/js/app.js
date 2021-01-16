$(document).ready(() => {
    manageNotifications();
});

function manageNotifications() {
    $.ajax({
        url: "/notifications/subscribe",
        timeout: 30000,
        success: showNotifications,
        error: () => {},
        complete: (res) => {
            if (res.status !== 401) {
                manageNotifications();
            }
        }
    });
}

function showNotifications(data) {
    console.log(data);
    const notifications = data['notifications'];
    for (const notification of notifications) {
        const content = notification.content;
        const timestamp = notification.timestamp;
        const id = notification.id;
        $('#notification-container').append(
            `<div class="notification" data-value="${id}">
                <div class="notification-cross" data-value="${id}">X</div>
                <h3>${content}</h3>
                <i>${timestamp}</i>
            </div>`
        );
    }
    $('.notification-cross').on('click', e => {
        const data_value = $(e.target).attr('data-value');
        $(`.notification[data-value="${data_value}"]`).remove();
    })
}
