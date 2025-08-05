 // Task filtering functionality
        $(document).ready(function() {
            // Search filter
            $('#taskSearch').on('keyup', function() {
                const searchText = $(this).val().toLowerCase();
                $('.task-item').each(function() {
                    const taskText = $(this).text().toLowerCase();
                    $(this).toggle(taskText.includes(searchText));
                });
            });

            // Status filter
            $('#statusFilter').on('change', function() {
                const status = $(this).val();
                if (status === '') {
                    $('.task-item').show();
                } else {
                    $('.task-item').each(function() {
                        const taskStatus = $(this).data('status');
                        $(this).toggle(taskStatus === status);
                    });
                }
            });
        });