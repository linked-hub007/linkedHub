// Activate the first tab if none is active
if (window.location.hash) {
    const tabTrigger = new bootstrap.Tab(document.querySelector(`a[href="${window.location.hash}"]`));
    tabTrigger.show();
}

// Update URL hash when tabs are shown
document.querySelectorAll('a[data-bs-toggle="pill"]').forEach(tab => {
    tab.addEventListener('shown.bs.tab', function (e) {
        window.location.hash = e.target.getAttribute('href');
    });
});