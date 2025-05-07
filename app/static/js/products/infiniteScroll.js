
class InfiniteScrollController {
  static config = {
    mobileBreakpoint: 768,
    desktopRootMargin: '200px',
    mobileRootMargin: '400px',
    loaderId: 'infinite-scroll-loader',
    endPageId: 'end-page'
  };

  static state = {
    isLoading: false,
    hasMoreProducts: true
  };

  /**
   * Initialize infinite scroll system
   */
  static initialize() {
    document.addEventListener('DOMContentLoaded', () => this.setupObserver());
    window.addEventListener('load', this.adjustViewport);
    window.addEventListener('resize', this.adjustViewport);
  }
  /**  Get additional filters
   * like size
  */
  static getAdditionalFilters(){
    const params = new URLSearchParams();
    document.querySelectorAll('#filters-container input:checked').forEach(input => {
      params.append(input.id.split('-')[0], input.value);
    });
    return params.toString();
  }
  /**
   * Set up intersection observer with responsive settings
   */
  static setupObserver() {
    const trigger = this.createLoaderElement();
    const isMobile = window.matchMedia(`(max-width: ${this.config.mobileBreakpoint}px)`).matches;

    const observer = new IntersectionObserver(
      entries => this.handleIntersection(entries),
      {
        root: null,
        rootMargin: isMobile ? this.config.mobileRootMargin : this.config.desktopRootMargin,
        threshold: 0
      }
    );

    observer.observe(trigger);
    console.log(`Infinite scroll initialized (${isMobile ? 'mobile' : 'desktop'} mode)`);
  }

  /**
   * Create loader element if it doesn't exist
   */
  static createLoaderElement() {
    let trigger = document.getElementById(this.config.loaderId);
    
    if (!trigger) {
      trigger = document.createElement('div');
      trigger.id = this.config.loaderId;
      trigger.className = 'infinite-scroll-trigger hidden';
      trigger.style.height = '100px';
      trigger.style.width = '100%';
      document.getElementById(this.config.endPageId)?.appendChild(trigger);
    }
    
    return trigger;
  }

  /**
   * Handle intersection observer events
   */
  static handleIntersection(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting && !this.state.isLoading && this.state.hasMoreProducts) {
        console.log('Trigger element visible - loading more');

        const meta = ProductMetaTracker.get();
        const page =  Math.floor(ProductRenderer.getProductCount()/meta.per_page) +1;
        if (page === meta.page){
          this.state.isLoading = false;
          this.state.hasMoreProducts = false;
          return;
        }
        this.loadMoreProducts();
      }
    });
  }

  /**
   * Load more products from API
   */
  static async loadMoreProducts() {
    this.state.isLoading = true;
    const trigger = document.getElementById(this.config.loaderId);
    
    try {
      this.showLoadingState(trigger);
      const apiUrl = this.buildApiUrl();

      console.log('Fetching from ' + apiUrl);
      const response = await fetch(apiUrl);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      console.log('Received products:', data.data?.length || 0);

      this.handleResponse(data, trigger);
    } catch (error) {
      this.handleError(error, trigger);
    } finally {
      this.state.isLoading = false;
    }
  }

  /**
   * Build API URL based on current route
   */
  static buildApiUrl() {
    const currentOffset = ProductRenderer.getProductCount();
    const path = window.location.pathname;
    let apiUrl;

    if (path.includes('/categories/')) {
      const category = path.split('/categories/')[1].split('/')[0];
      apiUrl = `/products/categories/${category}?page=${Math.floor(currentOffset/12) + 1}`;
    } else {
      const meta = ProductMetaTracker.get();
      console.log(`Loaded page ${meta.page} of ${meta.total_pages}`);
      
      apiUrl = `/products/q?page=${Math.floor(currentOffset/meta.per_page) + 1}`;
    }

    const additionalFilters = this.getAdditionalFilters();
    if  (additionalFilters){
      apiUrl += "&"+additionalFilters;
      console.log("Additional filtes detected : "+apiUrl);

    }
    return apiUrl;
  }

  /**
   * Update UI for loading state
   */
  static showLoadingState(trigger) {
    trigger.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
  }

  /**
   * Handle successful API response
   */
  static handleResponse(data, trigger) {
    // On receiving metadata from API
    ProductMetaTracker.update(data.meta);
    if (data.data?.length > 0) {
      ProductRenderer.renderProducts(data.data, true);
    } else {
      this.state.hasMoreProducts = false;
      trigger.innerHTML = '<p class="text-muted text-center py-3">End of products</p>';
    }
  }

  /**
   * Handle API errors
   */
  static handleError(error, trigger) {
    console.error('Load error:', error);
    trigger.innerHTML = '<p class="text-danger text-center py-3">Load error. Scroll to try again.</p>';
    this.state.hasMoreProducts = true; // Allow retry
  }

  /**
   * Mobile viewport adjustment
   */
  static adjustViewport() {
    if (window.matchMedia(`(max-width: $768px)`).matches) {
      document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
    }
  }
}

InfiniteScrollController.initialize();