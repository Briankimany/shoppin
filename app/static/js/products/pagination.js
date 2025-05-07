class Pagination {
    static render(meta) {
      const pagination = document.getElementById('pagination');
      pagination.innerHTML = '';
  
      // Previous button
      pagination.innerHTML += `
        <li class="page-item ${meta.page === 1 ? 'disabled' : ''}">
          <a class="page-link" href="#" data-page="${meta.page - 1}">
            <i class="ni ni-bold-left"></i>
          </a>
        </li>
      `;
  
      // Page numbers
      for (let i = 1; i <= meta.total_pages; i++) {
        pagination.innerHTML += `
          <li class="page-item ${i === meta.page ? 'active' : ''}">
            <a class="page-link" href="#" data-page="${i}">${i}</a>
          </li>
        `;
      }
  
      // Next button
      pagination.innerHTML += `
        <li class="page-item ${meta.page === meta.total_pages ? 'disabled' : ''}">
          <a class="page-link" href="#" data-page="${meta.page + 1}">
            <i class="ni ni-bold-right"></i>
          </a>
        </li>
      `;
    }
  }