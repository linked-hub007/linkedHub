// Set current year in footer
        document.addEventListener('DOMContentLoaded', function() {
            const displayYear = document.getElementById('displayYear');
            if (displayYear) {
                displayYear.textContent = new Date().getFullYear();
            }

            // Handle checkbox validation
            const termsCheckbox = document.getElementById('termsCheckbox');
            const signupBtn = document.getElementById('signupBtn');
            const googleBtn = document.getElementById('googleBtn');

            function toggleButtons() {
                if (termsCheckbox.checked) {
                    signupBtn.disabled = false;
                    googleBtn.classList.remove('disabled-link');
                    googleBtn.style.pointerEvents = 'auto';
                } else {
                    signupBtn.disabled = true;
                    googleBtn.classList.add('disabled-link');
                    googleBtn.style.pointerEvents = 'none';
                }
            }

            // Initial state
            toggleButtons();

            // Listen for checkbox changes
            termsCheckbox.addEventListener('change', toggleButtons);

            // Prevent Google login if terms not accepted
            googleBtn.addEventListener('click', function(e) {
                if (!termsCheckbox.checked) {
                    e.preventDefault();
                    alert('Please accept the Terms of Service and Privacy Policy to continue.');
                    return false;
                }
            });

            // Prevent form submission if terms not accepted
            document.querySelector('.signup').addEventListener('submit', function(e) {
                if (!termsCheckbox.checked) {
                    e.preventDefault();
                    alert('Please accept the Terms of Service and Privacy Policy to continue.');
                    return false;
                }
            });
        });