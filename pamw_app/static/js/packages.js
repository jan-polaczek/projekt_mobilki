$(document).ready(() => {
    setupDeleteButtons();
});

function setupDeleteButtons() {
    $('.delete-package-button').on('click', (e) => {
        const id = e.target.closest('svg').id;
        const row = $(e.target).closest('tr');
        $.ajax({
            url: '/api/packages/' + id,
            type: 'DELETE',
            success: () => {
                row.remove();
            }
        })
    });
}
