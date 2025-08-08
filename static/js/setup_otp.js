document.addEventListener('DOMContentLoaded', function() {
    const logoImage = document.querySelector('.logo-image');
    if (logoImage) {
        logoImage.addEventListener('error', function() {
            this.style.display = 'none';
         });
         logoImage.addEventListener('load', function() {
            this.style.display = 'block';
            this.parentElement.classList.add('has-image');
        });
    }
});
