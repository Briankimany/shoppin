
    document.addEventListener('DOMContentLoaded', function() {
    const mainNav = document.getElementById('mainNav');
    const navToggle = document.querySelector('.nav-toggle');
    const collapseToggle = document.querySelector('.collapse-toggle');
    
    // Track mobile state
    let isMobileMenuOpen = false;

    // Mobile Toggle
    navToggle?.addEventListener('click', function(e) {
        e.stopPropagation();
        isMobileMenuOpen = !mainNav.classList.contains('mobile-open');
        mainNav.classList.toggle('mobile-open', isMobileMenuOpen);
        document.body.classList.toggle('nav-open', isMobileMenuOpen);
    });

    // Collapse/Expand Toggle
    collapseToggle?.addEventListener('click', function(e) {
        e.stopPropagation();
        const isCollapsed = !mainNav.classList.contains('collapsed');
        mainNav.classList.toggle('collapsed', isCollapsed);
        localStorage.setItem('vendorNavCollapsed', isCollapsed);
        
        // Update chevron icon
        const icon = this.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-chevron-left', !isCollapsed);
            icon.classList.toggle('fa-chevron-right', isCollapsed);
        }
    });

    // Restore collapsed state
    if (localStorage.getItem('vendorNavCollapsed') === 'true') {
        mainNav.classList.add('collapsed');
    }

    // Dropdown functionality
    document.querySelectorAll('.dropdown-header').forEach(header => {
        header.addEventListener('click', function(e) {
            e.stopPropagation();
            const parent = this.closest('.has-dropdown');
            const isOpening = !parent.classList.contains('open');
            parent.classList.toggle('open', isOpening);
            
            // Close other dropdowns when opening a new one
            if (isOpening) {
                document.querySelectorAll('.has-dropdown.open').forEach(dropdown => {
                    if (dropdown !== parent) {
                        dropdown.classList.remove('open');
                    }
                });
            }
        });
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        // Close mobile menu if open and clicking outside
        if (isMobileMenuOpen && !mainNav.contains(e.target)) {
            mainNav.classList.remove('mobile-open');
            document.body.classList.remove('nav-open');
            isMobileMenuOpen = false;
        }
        
        // Close dropdowns when clicking outside (original functionality)
        if (!e.target.closest('.has-dropdown')) {
            document.querySelectorAll('.has-dropdown.open').forEach(dropdown => {
                dropdown.classList.remove('open');
            });
        }
    });

    // Quick actions
    function redirectTo(element) {
        const href = element.getAttribute('data-href');
        if (href) window.location.href = href;
    }
    window.redirectTo = redirectTo;

    function redirectToNewTab(element) {
        const url = element.getAttribute('data-href');
        window.open(url, '_blank');
    }
    window.redirectToNewTab = redirectToNewTab

    // Responsive adjustments
    function handleResize() {
        if (window.innerWidth >= 992) {
            // Close mobile menu on desktop
            if (mainNav.classList.contains('mobile-open')) {
                mainNav.classList.remove('mobile-open');
                document.body.classList.remove('nav-open');
                isMobileMenuOpen = false;
            }
        }
    }

    // Debounced resize handler
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 100);
    });

    // Close menu when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isMobileMenuOpen) {
            mainNav.classList.remove('mobile-open');
            document.body.classList.remove('nav-open');
            isMobileMenuOpen = false;
        }
    });
});

