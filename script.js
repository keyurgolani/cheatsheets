document.addEventListener("DOMContentLoaded", () => {
  // Theme Management
  const themeToggle = document.getElementById("theme-toggle");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    updateThemeIcon(theme);
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    const icon = themeToggle.querySelector('i');
    if (icon) {
      icon.className = theme === 'dark' ? 'ph ph-sun' : 'ph ph-moon';
    }
    themeToggle.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
  }

  // Initialize Theme
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    setTheme(savedTheme);
  } else {
    setTheme(prefersDark.matches ? "dark" : "light");
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const currentTheme = document.documentElement.getAttribute("data-theme");
      setTheme(currentTheme === "dark" ? "light" : "dark");
    });
  }

    // Search Functionality
    const searchInput = document.querySelector('.search-input');
    const isHomepage = window.location.pathname.endsWith('index.html') || window.location.pathname.endsWith('/');
    
    if (searchInput) {
        if (isHomepage) {
            // Global Search (Homepage)
            const resultsGrid = document.createElement('div');
            resultsGrid.className = 'search-results-grid';
            const categoriesGrid = document.querySelector('.categories-grid');
            categoriesGrid.parentNode.insertBefore(resultsGrid, categoriesGrid);
            
            let searchIndex = [];
            
            // Load search index
            fetch('search_index.json')
                .then(response => response.json())
                .then(data => {
                    searchIndex = data;
                })
                .catch(err => console.error('Failed to load search index:', err));
            
            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                
                if (searchTerm.length < 2) {
                    categoriesGrid.style.display = 'grid';
                    resultsGrid.style.display = 'none';
                    return;
                }
                
                const results = searchIndex.filter(item => 
                    item.title.toLowerCase().includes(searchTerm) || 
                    item.section.toLowerCase().includes(searchTerm) || 
                    item.content.toLowerCase().includes(searchTerm)
                ).slice(0, 20); // Limit results
                
                if (results.length > 0) {
                    categoriesGrid.style.display = 'none';
                    resultsGrid.style.display = 'grid';
                    resultsGrid.innerHTML = results.map(item => `
                        <a href="${item.url}" class="search-result-card">
                            <div class="result-path">${item.title} > ${item.section}</div>
                            <h3>${item.section}</h3>
                            <div class="result-context">${item.content.substring(0, 150)}...</div>
                        </a>
                    `).join('');
                } else {
                    categoriesGrid.style.display = 'none';
                    resultsGrid.style.display = 'block';
                    resultsGrid.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No results found.</p>';
                }
            });
        } else {
            // Local Search (Cheatsheet Page)
            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                const cards = document.querySelectorAll('.card');
                
                cards.forEach(card => {
                    const text = card.textContent.toLowerCase();
                    const isVisible = text.includes(searchTerm);
                    card.style.display = isVisible ? 'flex' : 'none';
                });
                
                // Re-trigger masonry layout if needed (CSS columns handle it automatically mostly)
            });
        }
    }

  // Copy to Clipboard
  const codeBlocks = document.querySelectorAll(".code-block");
  codeBlocks.forEach((block) => {
    const copyBtn = document.createElement("button");
    copyBtn.className = "copy-btn";
    copyBtn.textContent = "Copy";
    copyBtn.addEventListener("click", async () => {
      const code = Array.from(block.querySelectorAll(".code-line"))
        .map((line) => line.textContent)
        .join("\n");

      try {
        await navigator.clipboard.writeText(code);
        copyBtn.textContent = "Copied!";
        setTimeout(() => (copyBtn.textContent = "Copy"), 2000);
      } catch (err) {
        console.error("Failed to copy:", err);
        copyBtn.textContent = "Error";
      }
    });
    block.appendChild(copyBtn);
  });

  // Download PDF
  const downloadBtn = document.getElementById("download-btn");
  if (downloadBtn) {
    downloadBtn.addEventListener("click", () => {
      window.print();
    });
  }
});
