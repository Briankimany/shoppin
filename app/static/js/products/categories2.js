class CategoryManager {
    static init() {
      this.setupBaseStructure();
      this.loadCategories();
      this.setupEventListeners();
    }
  
    static setupBaseStructure() {
      // Create mobile modal backdrop if it doesn't exist
      if (!document.getElementById('category-modal-backdrop')) {
        document.body.insertAdjacentHTML('beforeend', `
          <div class="category-modal-backdrop" id="category-modal-backdrop"></div>
        `);
      }
    }
  
    static async loadCategories() {
      try {
        const response = await fetch('/products/categories');
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        
        const data= await response.json();
        this.renderDesktopCategories(data);
        this.renderMobileCategories(data);
        this.updateActiveStates();
      } catch (error) {
        console.error('CategoryManager error:', error);
        this.showErrorState();
      }
    }
  
    static renderDesktopCategories(categories) {
      const container = document.getElementById('desktop-categories');
      container.innerHTML = this.createCategoryList(categories, 0, true);
    }
  
    static renderMobileCategories(categories) {
      const container = document.getElementById('mobile-categories');
      container.innerHTML = this.createCategoryList(categories, 0, false);
    }
  
    static createCategoryList(categories, level = 0, isDesktop = true) {
      return `
        <ul class="category-list ${level > 0 ? 'subcategory-list' : ''}">
          ${Object.entries(categories).map(([name, subcategories]) => {
            const hasChildren = typeof subcategories === 'object' && !Array.isArray(subcategories);
            
            return `
              <li class="category-item ${hasChildren ? 'has-children' : ''}">
                ${hasChildren ? `
                  <button class="category-link" 
                          data-category="${name}" 
                          data-level="${level}"
                          ${isDesktop ? '' : 'data-mobile-modal'}>
                    <span>${name}</span>
                    <i class="ni ni-bold-right"></i>
                  </button>
                  ${isDesktop ? this.createCategoryList(subcategories, level + 1, true) : ''}
                ` : `
                  <a href="/products/categories/${encodeURIComponent(name)}" class="category-link">
                    ${name}
                  </a>
                `}
              </li>
            `;
          }).join('')}
        </ul>
      `;
    }
  
    static setupEventListeners() {
      // Desktop hover events
      document.querySelectorAll('#desktop-categories .category-link[data-category]').forEach(link => {
        link.addEventListener('mouseenter', (e) => {
          const categoryItem = e.currentTarget.closest('.category-item');
          const sublist = categoryItem.querySelector('.subcategory-list');
          
          if (sublist) {
            // Hide all other sublists at this level
            categoryItem.parentElement.querySelectorAll('.subcategory-list').forEach(list => {
              if (list !== sublist) list.style.display = 'none';
            });
            
            // Position and show current sublist
            const rect = categoryItem.getBoundingClientRect();
            sublist.style.display = 'block';
            sublist.style.left = `${rect.right + 10}px`;
            sublist.style.top = `${rect.top}px`;
          }
        });
      });
  
      // Mobile click events
      document.querySelectorAll('[data-mobile-modal]').forEach(button => {
        button.addEventListener('click', (e) => {
          const category = e.currentTarget.dataset.category;
          const level = parseInt(e.currentTarget.dataset.level) + 1;
          
          // Fetch subcategories (in real app you might want to pre-load these)
          const subcategories = this.getSubcategories(category);
          this.showMobileModal(category, subcategories, level);
        });
      });
  
      // Close modal when clicking backdrop
      document.getElementById('category-modal-backdrop').addEventListener('click', () => {
        this.hideMobileModal();
      });
    }
  
    static showMobileModal(title, categories, level) {
      const modal = document.createElement('div');
      modal.className = 'category-modal';
      modal.style.transform = `translateX(${100 * level}%)`;
      modal.innerHTML = `
        <div class="category-modal-header">
          <button class="back-button" data-level="${level}">
            <i class="ni ni-bold-left"></i>
          </button>
          <h5>${title}</h5>
        </div>
        <div class="category-modal-body">
          ${this.createCategoryList(categories, level, false)}
        </div>
      `;
      
      document.body.appendChild(modal);
      document.getElementById('category-modal-backdrop').style.display = 'block';
      
      // Animate in
      setTimeout(() => {
        modal.style.transform = `translateX(${100 * (level - 1)}%)`;
      }, 10);
    }
  
    static hideMobileModal() {
      const modals = document.querySelectorAll('.category-modal');
      const backdrop = document.getElementById('category-modal-backdrop');
      
      // Animate out
      modals.forEach(modal => {
        const level = parseInt(modal.querySelector('.back-button')?.dataset.level || 1);
        modal.style.transform = `translateX(${100 * level}%)`;
        
        setTimeout(() => {
          modal.remove();
          if (modals.length === 1) backdrop.style.display = 'none';
        }, 300);
      });
    }
  
    static addCategoryItem(container, href, text, level = 0) {
        const item = document.createElement('a');
        item.href = href;
        item.className = `category-nav-item d-block ${level > 0 ? `pl-${level + 3}` : ''}`;
        item.textContent = text;
        container.appendChild(item);
      }
    
      static updateActiveStates() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.category-nav-item').forEach(item => {
          const itemPath = item.getAttribute('href');
          
          // Check if current path matches or is a subcategory
          if (currentPath === itemPath || 
              (itemPath !== '/' && currentPath.includes(itemPath))) {
            item.classList.add('active');
            
            // Expand parent dropdowns
            let parent = item.closest('.collapse');
            while (parent) {
              const toggle = document.querySelector(`[data-bs-target="#${parent.id}"]`);
              if (toggle) {
                new bootstrap.Collapse(parent, { toggle: true });
                toggle.classList.add('active');
              }
              parent = parent.parentElement.closest('.collapse');
            }
          }
        });
      }
    
      static updateCategoryTitle() {
        const pathParts = window.location.pathname.split('/');
        const titleElement = document.getElementById('current-category-title');
        
        if (pathParts.includes('categories') && pathParts.length > 3) {
          titleElement.textContent = decodeURIComponent(pathParts[3]);
        } else {
          titleElement.textContent = 'All Products';
        }
      }
    
      static showErrorState() {
        const containers = [
          document.getElementById('desktop-categories'),
          document.getElementById('mobile-categories')
        ];
        
        containers.forEach(container => {
          if (container) {
            container.innerHTML = `
              <div class="alert alert-danger">
                Failed to load categories. <a href="javascript:location.reload()">Try again</a>.
              </div>
            `;
          }
        });
      }
    
      static setupEventListeners() {
        // Initialize Bootstrap collapse components
        document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(toggle => {
          toggle.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon) {
              icon.classList.toggle('ni-bold-down');
              icon.classList.toggle('ni-bold-up');
            }
          });
        });
      }
    }
    
    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', () => CategoryManager.init());