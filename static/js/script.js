// Simple JavaScript for the Lost and Found website

document.addEventListener('DOMContentLoaded', function() {
    // Form validation for login
    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const userIdInput = document.getElementById('user_id');
            if (userIdInput && !userIdInput.value.trim()) {
                e.preventDefault();
                alert('Please enter your unique ID');
                userIdInput.focus();
                return false;
            }
        });
    }
    
    // Confirmation for delete actions (would be expanded in a full implementation)
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this report?')) {
                e.preventDefault();
            }
        });
    });
    
    // Toggle password visibility for admin login
    const togglePassword = document.querySelector('#togglePassword');
    const passwordInput = document.querySelector('#password');
    
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.textContent = type === 'password' ? '👁️' : '🔒';
        });
    }
});

// Function to show/hide search form on mobile
function toggleSearchForm() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.classList.toggle('hidden');
    }
}