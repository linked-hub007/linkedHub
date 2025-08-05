/**
 * Study Materials Page JavaScript
 * Fixed version with better error handling and authentication checks
 */

// Main filtering function
function filterMaterials() {
    // Get all filter values
    const searchInput = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const materialType = document.getElementById('materialTypeFilter')?.value || '';
    const category = document.getElementById('categoryFilter')?.value || '';
    const assignedPlace = document.getElementById('assignedPlaceFilter')?.value.toLowerCase() || '';
    const author = document.getElementById('authorFilter')?.value.toLowerCase() || '';
    const dateFilter = document.getElementById('dateFilter')?.value || '';
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const cards = document.querySelectorAll('.material-card');
    let visibleCount = 0;
    
    cards.forEach(card => {
        // Get card data safely
        const titleElement = card.querySelector('.material-title');
        const title = titleElement ? titleElement.textContent.toLowerCase() : '';
        
        const cardType = card.dataset.type || '';
        const cardCategory = card.dataset.category || '';
        const cardLocation = (card.dataset.location || '').toLowerCase();
        const cardAuthor = (card.dataset.author || '').toLowerCase();
        const uploadDateStr = card.dataset.uploadDate;
        
        // Parse upload date safely
        let uploadDate = new Date();
        if (uploadDateStr) {
            uploadDate = new Date(uploadDateStr);
            // If date is invalid, use current date
            if (isNaN(uploadDate.getTime())) {
                uploadDate = new Date();
            }
        }
        
        // Check all filter conditions
        const matchesSearch = searchInput === '' || title.includes(searchInput);
        const matchesType = materialType === '' || cardType === materialType;
        const matchesCategory = category === '' || cardCategory === category;
        const matchesLocation = assignedPlace === '' || cardLocation.includes(assignedPlace);
        const matchesAuthor = author === '' || cardAuthor.includes(author);
        
        // Check date filter
        let matchesDate = true;
        if (dateFilter !== '') {
            const diffTime = today - uploadDate;
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
            
            switch(dateFilter) {
                case 'today':
                    matchesDate = diffDays <= 0;
                    break;
                case 'week':
                    matchesDate = diffDays <= 7;
                    break;
                case 'month':
                    matchesDate = diffDays <= 30;
                    break;
                case 'year':
                    matchesDate = diffDays <= 365;
                    break;
                default:
                    matchesDate = true;
            }
        }
        
        // Show or hide card based on all filters
        if (matchesSearch && matchesType && matchesCategory && 
            matchesLocation && matchesAuthor && matchesDate) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show/hide empty state message
    showEmptyState(visibleCount === 0);
}

// Show empty state when no materials match filters
function showEmptyState(show) {
    const materialsGrid = document.getElementById('materials-content');
    if (!materialsGrid) return;
    
    let emptyState = materialsGrid.querySelector('.empty-state-filter');
    
    if (show && !emptyState) {
        // Create empty state for filtered results
        emptyState = document.createElement('div');
        emptyState.className = 'empty-state empty-state-filter';
        emptyState.innerHTML = `
            <div style="text-align: center; padding: 40px 20px; color: #666;">
                <i class="fas fa-search" style="font-size: 48px; margin-bottom: 20px; color: #ddd;"></i>
                <h3 style="margin-bottom: 15px; font-size: 24px;">No Materials Found</h3>
                <p style="margin-bottom: 25px; font-size: 16px;">Try adjusting your filters or search terms to find what you're looking for.</p>
                <button class="action-btn btn-open" onclick="resetFilters()" style="margin-top: 20px; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    <i class="fas fa-refresh"></i>
                    Clear Filters
                </button>
            </div>
        `;
        materialsGrid.appendChild(emptyState);
    } else if (!show && emptyState) {
        emptyState.remove();
    }
}

// Reset all filters to default state
function resetFilters() {
    // Reset all filter inputs
    const searchInput = document.getElementById('searchInput');
    const materialTypeFilter = document.getElementById('materialTypeFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const assignedPlaceFilter = document.getElementById('assignedPlaceFilter');
    const authorFilter = document.getElementById('authorFilter');
    const dateFilter = document.getElementById('dateFilter');
    
    if (searchInput) searchInput.value = '';
    if (materialTypeFilter) materialTypeFilter.value = '';
    if (categoryFilter) categoryFilter.value = '';
    if (assignedPlaceFilter) assignedPlaceFilter.value = '';
    if (authorFilter) authorFilter.value = '';
    if (dateFilter) dateFilter.value = '';
    
    // Reapply filters (which will show all items)
    filterMaterials();
}

// Show notification messages
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        z-index: 9999;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease-out;
    `;
    
    // Set background color based on type
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#28a745';
            break;
        case 'error':
            notification.style.backgroundColor = '#dc3545';
            break;
        case 'warning':
            notification.style.backgroundColor = '#ffc107';
            notification.style.color = '#000';
            break;
        default:
            notification.style.backgroundColor = '#007bff';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Get CSRF token from cookies or DOM
function getCSRFToken() {
    // First try to get from DOM
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    // Fallback to cookie method
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    return cookieValue || '';
}

// Smooth scroll to element
function smoothScroll(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Study Material page loaded');
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    // Set current year in footer
    const displayYear = document.getElementById('displayYear');
    if (displayYear) {
        displayYear.textContent = new Date().getFullYear();
    }
    
    // Handle role buttons
    const taskBtn = document.getElementById('taskBtn');
    const studyBtn = document.getElementById('studyBtn');
    
    if (studyBtn) {
        studyBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({ 
                top: 0, 
                behavior: 'smooth' 
            });
        });
    }
    
    // Initialize filters
    setTimeout(() => {
        filterMaterials();
    }, 100);
    
    // Add smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            smoothScroll(targetId);
        });
    });
    
    // Add keyboard support for search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                filterMaterials();
            }
        });
    }
    
    // Add hover effects to material cards
    const materialCards = document.querySelectorAll('.material-card');
    materialCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
    
    console.log('All event listeners attached successfully');
});