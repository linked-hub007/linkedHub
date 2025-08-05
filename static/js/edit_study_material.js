 // File size validation
        document.getElementById('file').addEventListener('change', function(e) {
            const file = e.target.files[0];
            const materialType = document.getElementById('material_type').value;
            const maxSize = materialType === 'pdf' ? 20 * 1024 * 1024 : 5 * 1024 * 1024;
            
            if (file && file.size > maxSize) {
                alert(`File size exceeds maximum allowed for ${materialType} (${materialType === 'pdf' ? '20MB' : '5MB'})`);
                e.target.value = '';
            }
        });
        
        // Update max size hint when material type changes
        document.getElementById('material_type').addEventListener('change', function() {
            const hint = document.querySelector('.form-text');
            const maxSize = this.value === 'pdf' ? '20MB' : '5MB';
            hint.textContent = `Leave blank to keep current file. Max size: ${maxSize}`;
        });