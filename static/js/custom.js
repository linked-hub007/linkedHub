// Enhanced Mobile Menu Handling
document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const navbarCollapse = document.querySelector('.custom_nav-container .navbar-collapse');
  const navLinks = document.querySelectorAll('.custom_nav-container .nav-link');
  const navbarToggler = document.querySelector('.navbar-toggler');
  const navbarTogglerIcon = document.querySelector('.navbar-toggler-icon');

  // Variables
  let lastScrollPosition = 0;

  // Close menu function (now also resets the toggle icon)
  const closeMobileMenu = () => {
    if (navbarCollapse.classList.contains('show')) {
      navbarCollapse.classList.remove('show');
      document.body.classList.remove('menu-open');
      if (navbarToggler) {
        navbarToggler.setAttribute('aria-expanded', 'false');
        // Reset the icon transform
        if (navbarTogglerIcon) {
          navbarTogglerIcon.style.transform = 'rotate(0deg)';
        }
      }
    }
  };

  // Scroll handler
  window.addEventListener('scroll', function() {
    const currentScrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    
    if (navbarCollapse.classList.contains('show')) {
      closeMobileMenu();
    }
    
    lastScrollPosition = currentScrollPosition <= 0 ? 0 : currentScrollPosition;
  });

  // Close menu when clicking links
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      closeMobileMenu();
    });
  });

  // Handle toggle button click to properly track state
  if (navbarToggler) {
    navbarToggler.addEventListener('click', function() {
      const isExpanded = this.getAttribute('aria-expanded') === 'true';
      if (navbarTogglerIcon) {
        navbarTogglerIcon.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(90deg)';
      }
    });
  }
});

//gold
function toggleSubList(id) {
    const allSubLists = document.querySelectorAll('.sub-list');
    const clickedSubList = document.getElementById(id);
    const serviceIcon = clickedSubList.previousElementSibling.querySelector('i');
  
    // Close all other sub-lists
    allSubLists.forEach((list) => {
      if (list.id !== id) {
        list.classList.remove('active');
        list.previousElementSibling.querySelector('i').style.transform = 'rotate(0deg)';
      }
    });
  
    // Toggle the clicked sub-list
    clickedSubList.classList.toggle('active');
    if (clickedSubList.classList.contains('active')) {
      serviceIcon.style.transform = 'rotate(180deg)';
    } else {
      serviceIcon.style.transform = 'rotate(0deg)';
    }
  }
  
// to get current year
function getYear() {
    var currentDate = new Date();
    var currentYear = currentDate.getFullYear();
    document.querySelector("#displayYear").innerHTML = currentYear;
}

getYear();

// owl carousel 

$('.owl-carousel').owlCarousel({
    loop: true,
    margin: 10,
    nav: true,
    autoplay: true,
    autoplayHoverPause: true,
    responsive: {
        0: {
            items: 1
        },
        600: {
            items: 3
        },
        1000: {
            items: 6
        }
    }
})
//-------------------------------------------------------------------------------------------------//
