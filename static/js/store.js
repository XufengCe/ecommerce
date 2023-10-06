

// Smooth scrolling for anchor links

// Get the height of the navbar
const navbarHeight = document.querySelector('.navbar').offsetHeight;
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();

        const targetId = this.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
            // Calculate the scroll position with the navbar height offset
            const offset = targetElement.offsetTop - navbarHeight;

            window.scrollTo({
                top: offset,
                behavior: 'smooth'
            });
        }
    });
});


// Close the navbar when a navigation link is clicked
document.querySelectorAll('.navbar-nav .nav-link').forEach(function(navLink) {
    navLink.addEventListener('click', function() {
        var navbarToggler = document.querySelector('.navbar-toggler');
        if (navbarToggler) {
            navbarToggler.click();
            
            
        }
    });
});

