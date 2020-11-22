$(document).ready(() => {
    setupDeleteButtons();
});

function setupDeleteButtons() {
    $('.delete-package-button').on('click', (e) => {
        const id = e.target.id;
        const row = $(e.target).closest('tr');
        $.ajax({
            url: 'dashboard/' + id,
            type: 'DELETE',
            success: () => {
                row.remove();
            }
        })
    });
}
