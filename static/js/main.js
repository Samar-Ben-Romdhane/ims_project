document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.messages .alert');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
});

