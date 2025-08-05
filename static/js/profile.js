// Handle currently studying checkbox
document.querySelectorAll('[id^="currently_studying"]').forEach(checkbox => {
    const endDateId = checkbox.id.replace('currently_studying', 'end_date');
    const endDateInput = document.getElementById(endDateId);
            checkbox.addEventListener('change', function() {
                endDateInput.disabled = this.checked;
                if (this.checked) {
                    endDateInput.value = '';
                }
            });
            if (checkbox.checked) {
                endDateInput.disabled = true;
            }
        });
