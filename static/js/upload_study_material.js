// File upload preview
        document.getElementById('file').addEventListener('change', function(e) {
            const file = e.target.files[0];
            const preview = document.getElementById('filePreview');
            
            if (file) {
                preview.innerHTML = `
                    <div class="alert p-2">
                        <i class="fas fa-file me-2"></i>
                        <strong>${file.name}</strong> (${formatFileSize(file.size)})
                    </div>
                `;
            }
        });

        // Format file size
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
        }

        // Form validation
        document.querySelector('form').addEventListener('submit', function(e) {
            const fileInput = document.getElementById('file');
            if (fileInput.files.length === 0) {
                alert('Please select a file to upload');
                e.preventDefault();
            } else if (fileInput.files[0].size > 10 * 1024 * 1024) {
                alert('File size must be less than 10MB');
                e.preventDefault();
            }
        });