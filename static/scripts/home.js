
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('login_button').addEventListener('click', function() {
        window.location.href = '/login/';
    });

    document.getElementById('register_button').addEventListener('click', function() {
        window.location.href = '/register/';
    });

    document.getElementById('google_button').addEventListener('click', function() {
        window.location.href = '/authorize/';
    })
});
