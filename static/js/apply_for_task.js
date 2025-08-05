 // Character count functionality
        function updateCharacterCount(textarea) {
            const charCount = document.getElementById('charCount');
            charCount.textContent = textarea.value.length;
        }

        // Form validation and submission
        document.getElementById('applicationForm').addEventListener('submit', function(e) {
            const submitBtn = document.getElementById('submitBtn');
            const message = document.getElementById('message').value.trim();
            
            if (message.length < 20) {
                e.preventDefault();
                alert('Please write at least 20 characters to submit your application.');
                return;
            }
            
            // Add loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
            submitBtn.disabled = true;
        });

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Focus on textarea when page loads
            setTimeout(() => {
                document.getElementById('message').focus();
            }, 500);
        });