// Initialize tooltips
        $(document).ready(function(){
            $('[data-bs-toggle="tooltip"]').tooltip();
            
            // Set minimum date for deadline to today
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('deadline').min = today;
        });