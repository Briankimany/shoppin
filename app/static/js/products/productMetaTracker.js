
class ProductMetaTracker {
    static trackerId = 'product-meta-tracker';
  
    static ensureTrackerExists() {
      let tracker = document.getElementById(this.trackerId);
      if (!tracker) {
        tracker = document.createElement('div');
        tracker.id = this.trackerId;
        // tracker.style.display = 'none';
        document.body.appendChild(tracker);
      }
      return tracker;
    }
  
    static update(meta) {
      const tracker = this.ensureTrackerExists();
  
      if (!meta) return;
  
      tracker.dataset.total = meta.total || 0;
      tracker.dataset.page = meta.page || 1;
      tracker.dataset.perPage = meta.per_page || 0;
      tracker.dataset.totalPages = meta.total_pages || 1;
    }
  
    static get() {
      const tracker = document.getElementById(this.trackerId);
      if (!tracker) return null;
  
      return {
        total: parseInt(tracker.dataset.total || '0', 10),
        page: parseInt(tracker.dataset.page || '1', 10),
        per_page: parseInt(tracker.dataset.perPage || '0', 10),
        total_pages: parseInt(tracker.dataset.totalPages || '1', 10),
      };
    }
  }

