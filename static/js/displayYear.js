// Set current year in footer
document.addEventListener('DOMContentLoaded', function() {
    const displayYear = document.getElementById('displayYear');
    if (displayYear) {
        displayYear.textContent = new Date().getFullYear();
    }
});