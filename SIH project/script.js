
// Handles dynamic UI updates and basic client-side validation for sign-in/sign-up.
// Assumes Firebase logic is handled in the HTML file's <script type="module">.


document.addEventListener('DOMContentLoaded', () => {
    const roleSelect = document.getElementById('role');
    const phoneInput = document.getElementById('phoneNumber');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const loginSection = document.getElementById('login-section');
    const otpSection = document.getElementById('otp-section');
    const message = document.getElementById('message');

    // Dynamic placeholder and field toggling based on role
    roleSelect.addEventListener('change', () => {
        const role = roleSelect.value;
        message.innerText = '';
        if (role === 'Analyst') {
            phoneInput.style.display = 'none';
            document.querySelector('button[onclick="sendOTP()"]').style.display = 'none';
            emailInput.style.display = '';
            passwordInput.style.display = '';
            document.querySelector('button[onclick="signInEmail()"]').style.display = '';
            document.querySelector('button[onclick="signUpEmail()"]').style.display = '';
        } else {
            phoneInput.style.display = '';
            document.querySelector('button[onclick="sendOTP()"]').style.display = '';
            emailInput.style.display = '';
            passwordInput.style.display = '';
            document.querySelector('button[onclick="signInEmail()"]').style.display = '';
            document.querySelector('button[onclick="signUpEmail()"]').style.display = '';
        }
    });

    // Reset UI when user returns from OTP section
    function resetLoginUI() {
        loginSection.style.display = '';
        otpSection.style.display = 'none';
        message.innerText = '';
        document.getElementById('otpCode').value = '';
    }

    // Listen for successful login/signup to reset UI
    // (Assumes Firebase script sets message text on success)
    const observer = new MutationObserver(() => {
        if (message.innerText.includes('successful')) {
            setTimeout(resetLoginUI, 2000);
        }
    });
    observer.observe(message, { childList: true });

    // Basic phone input validation
    phoneInput.addEventListener('input', () => {
        phoneInput.value = phoneInput.value.replace(/\D/g, '').slice(0, 10);
    });

    // Optional: Enter key submits OTP
    document.getElementById('otpCode').addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            window.verifyOTP();
        }
    });
});