document.addEventListener('DOMContentLoaded', function() {
    // Initialize notification system
    const notification = document.getElementById('notification');
    const notificationContent = document.getElementById('notification-content');
    const notificationIcon = document.getElementById('notification-icon');
    const notificationClose = document.getElementById('notification-close');

    // Close notification when X is clicked
    notificationClose.addEventListener('click', hideNotification);


    // Enhanced Notification System
    function showNotification(type, message,duration=3500) {
        const notification = document.getElementById('notification');
        const notificationIcon = document.getElementById('notification-icon');
        const notificationContent = document.getElementById('notification-content');
        
        // Reset and set notification type
        notification.className = 'notification';
        notification.classList.add(type);
        
        // Set icon based on type
        switch(type) {
            case 'success':
                notificationIcon.className = 'fas fa-check';
                break;
            case 'error':
                notificationIcon.className = 'fas fa-exclamation';
                break;
            case 'warning':
                notificationIcon.className = 'fas fa-exclamation-triangle';
                break;
        }
        
        notificationContent.textContent = message;
        notification.classList.add('show');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
        }, duration);
    }

    // Close notification when X is clicked
    document.getElementById('notification-close').addEventListener('click', function() {
        document.getElementById('notification').classList.remove('show');
    });

    // Scroll-aware Navigation Bar
    document.addEventListener('DOMContentLoaded', function() {
        const navbar = document.querySelector('.navbar');
        let lastScroll = 0;
        
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll <= 0) {
                // At top of page
                navbar.classList.remove('hide');
                navbar.classList.add('show');
                return;
            }
            
            if (currentScroll > lastScroll && !navbar.classList.contains('hide')) {
                // Scrolling down
                navbar.classList.remove('show');
                navbar.classList.add('hide');
            } else if (currentScroll < lastScroll && navbar.classList.contains('hide')) {
                // Scrolling up
                navbar.classList.remove('hide');
                navbar.classList.add('show');
            }
            
            lastScroll = currentScroll;
        });
    });


    function hideNotification() {
        notification.classList.remove('show');
    }

    // Exit intent notification
    document.addEventListener('mouseout', (e) => {
        if (e.clientY < 0) {
            showNotification('warning','Wait! Get priority review by applying now.');
        }
    });

    // FAQ Accordion Functionality
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const icon = question.querySelector('i');
        
        // Initialize all answers as closed
        answer.style.maxHeight = '0';
        answer.style.opacity = '0';
        answer.style.padding = '0 1.5rem';
        answer.style.overflow = 'hidden';
        
        question.addEventListener('click', () => {
            // Close all other open items
            faqItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    const otherAnswer = otherItem.querySelector('.faq-answer');
                    const otherIcon = otherItem.querySelector('.faq-question i');
                    
                    otherItem.classList.remove('active');
                    otherAnswer.style.maxHeight = '0';
                    otherAnswer.style.opacity = '0';
                    otherAnswer.style.padding = '0 1.5rem';
                    otherIcon.style.transform = 'rotate(0deg)';
                }
            });
            
            // Toggle current item
            item.classList.toggle('active');
            
            if (item.classList.contains('active')) {
                // Open this item
                answer.style.maxHeight = answer.scrollHeight + 'px';
                answer.style.opacity = '1';
                answer.style.padding = '0 1.5rem 1.5rem';
                icon.style.transform = 'rotate(180deg)';
            } else {
                // Close this item
                answer.style.maxHeight = '0';
                answer.style.opacity = '0';
                answer.style.padding = '0 1.5rem';
                icon.style.transform = 'rotate(0deg)';
            }
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Back to top button
    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('active');
            } else {
                backToTopBtn.classList.remove('active');
            }
        });
        
        backToTopBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            // Toggle menu visibility
            navLinks.classList.toggle('active');
            
            // Change icon
            const icon = this.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
                
                // Prevent body scroll when menu is open
                document.body.style.overflow = 'hidden';
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
                document.body.style.overflow = '';
            }
        });
        
        // Close menu when clicking on links
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                mobileMenuBtn.querySelector('i').classList.replace('fa-times', 'fa-bars');
                document.body.style.overflow = '';
            });
        });
    }

    // CSRF Token helper
    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]').content;
    }

    // Fill form with dummy data
    document.getElementById('fillDummyData')?.addEventListener('click', function() {
        const dummyData = {
            name: "John Doe",
            first_name: "John",
            second_name: "Doe",
            store_name: "Doe's Fresh Produce",
            email: "john.doe@example.com",
            phone: "0712345678",
            payment_type: "post_delivery",
            store_description: "We specialize in fresh organic fruits and vegetables sourced directly from local farmers.",
            plan_id: "1",  // Assuming this is a valid plan ID
            terms: "on"
        };

        // Fill in all form fields
        for (const [key, value] of Object.entries(dummyData)) {
            const element = document.querySelector(`[name="${key}"]`);
            if (!element) continue;

            if (element.type === 'checkbox') {
                element.checked = true;
            } else if (element.tagName === 'SELECT') {
                element.value = value;
            } else {
                element.value = value;
            }
        }
        showNotification('success', 'Dummy data filled');
    });

    // Form submission
    const form = document.getElementById('vendorContactForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const submitButton = form.querySelector('button[type="submit"]');
            
            // Disable submit button to prevent multiple submissions
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            
            try {
                const response = await fetch("submit-contact", {
                    method: 'POST',
                    body: formData,
                    headers: {
                        "X-CSRFToken": getCsrfToken()
                    }
                });
                
                const data = await response.json();
                
                if (data.message === 'success') {
                    showNotification('success', 'Application submitted successfully! Redirecting...',6000);

                } else if (data.message === 'warning') {
            
                    data.data.forEach(msg => {
                        showNotification('warning',msg,10000);
                    });
                   
                } else {
                    // showNotification('error', data.data || 'There was an error processing your application.',10000);
                    data.data.forEach(msg => {
                        showNotification('warning',msg,10000);
                    });
                }
                
            } catch (error) {
                showNotification('error', 'Network error occurred. Please try again.');
                console.error('Error:', error);
            } finally {
                // Re-enable submit button
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Application';
            }
        });
    }
});