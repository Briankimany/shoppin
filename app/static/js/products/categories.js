class CategoryManager {
  static init() {
    this.loadCategories();
    this.setupEventListeners();
  }

  static async loadCategories() {
    try {
      const response = await fetch('/products/categories');
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      
      const  data  = await response.json();
      this.renderCategories(data);
      this.updateActiveStates();
      this.updateCategoryTitle();
    } catch (error) {
      console.error('CategoryManager error:', error);
      this.showErrorState();
    }
  }

  static renderCategories(categories) {
    const desktopContainer = document.getElementById('desktop-categories');
    const mobileContainer = document.getElementById('mobile-categories');
    
    // Clear existing
    desktopContainer.innerHTML = '';
    mobileContainer.innerHTML = '';
    
    // Add "All Products" link
    this.addCategoryItem(desktopContainer, '/', 'All Products');
    this.addCategoryItem(mobileContainer, '/', 'All Products');
    
    // Render nested categories
    this.renderNestedCategories(desktopContainer, categories);
    this.renderNestedCategories(mobileContainer, categories);
  }

  static renderNestedCategories(container, categories, level = 0) {
    Object.entries(categories).forEach(([categoryName, subCategories]) => {
      if (typeof subCategories === 'object' && !Array.isArray(subCategories)) {
        // Parent category with dropdown
        const dropdownId = `dropdown-${categoryName.replace(/\s+/g, '-')}`;
        
        container.innerHTML += `
          <div class="category-dropdown">
            <button class="category-nav-item dropdown-toggle ${level > 0 ? 'pl-4' : ''}" 
                    type="button" 
                    data-bs-toggle="collapse" 
                    data-bs-target="#${dropdownId}"
                    aria-expanded="false">
              ${categoryName}
              <i class="ni ni-bold-down ms-1"></i>
            </button>
            <div id="${dropdownId}" class="collapse">
              ${this.renderSubcategories(subCategories, level + 1)}
            </div>
          </div>
        `;
      } else {
        // Leaf category (no children)
        const categoryPath = `/products/categories/${encodeURIComponent(categoryName)}`;
        this.addCategoryItem(container, categoryPath, categoryName, level);
      }
    });
  }

  static renderSubcategories(subCategories, level) {
    if (Array.isArray(subCategories)) {
      // Final level of subcategories
      return subCategories.map(category => `
        <a href="/products/categories/${encodeURIComponent(category)}" 
           class="category-nav-item d-block ${level > 1 ? 'pl-5' : 'pl-4'}">
          ${category}
        </a>
      `).join('');
    } else {
      // Nested object (more levels)
      let html = '';
      Object.entries(subCategories).forEach(([categoryName, children]) => {
        const dropdownId = `dropdown-${categoryName.replace(/\s+/g, '-')}`;
        
        html += `
          <div class="subcategory-group">
            <button class="category-nav-item dropdown-toggle d-block pl-4" 
                    type="button" 
                    data-bs-toggle="collapse" 
                    data-bs-target="#${dropdownId}"
                    aria-expanded="false">
              ${categoryName}
              <i class="ni ni-bold-down ms-1"></i>
            </button>
            <div id="${dropdownId}" class="collapse">
              ${this.renderSubcategories(children, level + 1)}
            </div>
          </div>
        `;
      });
      return html;
    }
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