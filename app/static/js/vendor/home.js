

document.addEventListener('mouseout', (e) => {
    if (e.clientY < 0) {
      showModal('Wait! Get priority review by applying now.');
    }
  });

  document.addEventListener('DOMContentLoaded', function() {
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

});

document.addEventListener('DOMContentLoaded', function() {
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
  });