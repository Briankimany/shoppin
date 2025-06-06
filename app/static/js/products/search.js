document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchSuggestions = document.getElementById('search-suggestions');
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      const query = this.value.trim();
      
      if (query.length > 2) {
        searchTimeout = setTimeout(() => {
          fetchSearchSuggestions(query);
        }, 300);
      } else {
        searchSuggestions.style.display = 'none';
      }
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
      if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
        searchSuggestions.style.display = 'none';
      }
    });
  });
  
  function fetchSearchSuggestions(query) {
    fetch(`/products/search/suggestions?q=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => {
        renderSearchSuggestions(data.data);
      })
      .catch(error => {
        console.error('Error fetching suggestions:', error);
      });
  }
  

  function renderSearchSuggestions(suggestions, query) {
    const container = document.getElementById('search-suggestions');
    container.innerHTML = '';
    
    if (suggestions.length === 0) {
      container.innerHTML = `
        <div class="search-suggestion-item text-muted">
          No results found for "${query}"
        </div>
      `;
    } else {
      suggestions.forEach(suggestion => {
        const highlightedName = highlightMatch(suggestion.name, query);
        const item = document.createElement('div');

        // In your render function:
        item.className = 'search-suggestion-item p-3 border-bottom hover-bg-light';
        item.innerHTML = `
          <div>${highlightedName}</div>
          <div class="search-suggestion-category">
            <i class="ni ni-tag me-1"></i>
            ${suggestion.category}
          </div>
        `;
        item.addEventListener('click', () => {
          window.location.href = `/products/product/${suggestion.id}`;
        });
        container.appendChild(item);
      });
    }
    container.classList.remove('d-none');
    container.style.display = 'block';
  }
  
  function highlightMatch(text, query) {
    if (!query) return text;
    const regex = new RegExp(query, 'gi');
    return text.replace(regex, match => 
      `<span class="search-suggestion-highlight">${match}</span>`
    );
  }

