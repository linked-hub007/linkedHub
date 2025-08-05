 // Form submission loading effect
        document.querySelector('.btn-primary').addEventListener('click', function(e) {
            const form = document.querySelector('form');
            if (form.checkValidity()) {
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating Task...';
            }
        });

        // Auto-resize textarea
        document.getElementById('description').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });

        // Set minimum date to today
        document.getElementById('deadline').min = new Date().toISOString().split('T')[0];