document.addEventListener('DOMContentLoaded', function() {
    // Display current year in footer
    const displayYear = document.getElementById('displayYear');
    if (displayYear) {
        displayYear.textContent = new Date().getFullYear();
    }
    // Get all task cards
    const taskCards = document.querySelectorAll('.task-card');
    
    // Get filter elements
    const searchInput = document.getElementById('searchInput');
    const moneyFilter = document.getElementById('moneyFilter');
    const taskStatusFilter = document.getElementById('taskStatusFilter');
    const assignedPlaceFilter = document.getElementById('assignedPlaceFilter');
    const deadlineFilter = document.getElementById('deadlineFilter');
    
    // Main filter function
    function filterTasks() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const moneyRange = moneyFilter ? moneyFilter.value.trim() : '';
        const statusFilter = taskStatusFilter ? taskStatusFilter.value : '';
        const assignedPlaceTerm = assignedPlaceFilter ? assignedPlaceFilter.value.toLowerCase() : '';
        const deadlineFilterValue = deadlineFilter ? deadlineFilter.value : '';
        
        const currentDate = new Date();
        currentDate.setHours(0, 0, 0, 0);
        
        let visibleCount = 0;
        
        taskCards.forEach(card => {
            const titleElement = card.querySelector('.task-title');
            const descriptionElement = card.querySelector('.task-description');
            const locationElement = card.querySelector('.location-badge');
            
            const title = titleElement ? titleElement.textContent.toLowerCase() : '';
            const description = descriptionElement ? descriptionElement.textContent.toLowerCase() : '';
            const assignedPlace = locationElement ? locationElement.textContent.toLowerCase() : '';
            
            const status = card.dataset.status || '';
            const deadlineStr = card.dataset.deadline || '';
            const budget = parseFloat(card.dataset.budget) || 0;
            
            // Check if card matches all filters
            const matchesSearch = !searchTerm || 
                                title.includes(searchTerm) || 
                                description.includes(searchTerm) || 
                                assignedPlace.includes(searchTerm);
            
            // Budget range filtering logic
            let matchesBudget = true;
            if (moneyRange) {
                const rangeParts = moneyRange.split('-');
                let min = 0;
                let max = Infinity;
                
                if (rangeParts.length === 2) {
                    min = parseFloat(rangeParts[0]) || 0;
                    max = parseFloat(rangeParts[1]) || Infinity;
                } else if (moneyRange.startsWith('>')) {
                    min = parseFloat(moneyRange.substring(1)) || 0;
                } else if (moneyRange.startsWith('<')) {
                    max = parseFloat(moneyRange.substring(1)) || Infinity;
                } else {
                    // Single value - treat as minimum
                    min = parseFloat(moneyRange) || 0;
                }
                
                matchesBudget = budget >= min && (max === Infinity || budget <= max);
            }
            
            const matchesStatus = !statusFilter || status === statusFilter;
            const matchesAssignedPlace = !assignedPlaceTerm || assignedPlace.includes(assignedPlaceTerm);
            
            // Deadline filtering logic
            let matchesDeadline = true;
            if (deadlineFilterValue && deadlineStr) {
                const deadlineDate = new Date(deadlineStr);
                deadlineDate.setHours(0, 0, 0, 0);
                
                switch(deadlineFilterValue) {
                    case 'today':
                        matchesDeadline = deadlineDate.getTime() === currentDate.getTime();
                        break;
                    case 'week':
                        const endOfWeek = new Date(currentDate);
                        endOfWeek.setDate(endOfWeek.getDate() + (6 - endOfWeek.getDay()));
                        matchesDeadline = deadlineDate >= currentDate && deadlineDate <= endOfWeek;
                        break;
                    case 'month':
                        const endOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
                        matchesDeadline = deadlineDate >= currentDate && deadlineDate <= endOfMonth;
                        break;
                    case 'future':
                        matchesDeadline = deadlineDate > currentDate;
                        break;
                }
            }
            
            // Show/hide card based on filters
            if (matchesSearch && matchesBudget && matchesStatus && 
                matchesAssignedPlace && matchesDeadline) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Show empty state if no tasks are visible
        const emptyState = document.querySelector('#task-content .empty-state');
        if (emptyState) {
            emptyState.style.display = visibleCount === 0 ? 'flex' : 'none';
        }
    }
    
    // Reset all filters function
    function resetFilters() {
        if (searchInput) searchInput.value = '';
        if (moneyFilter) moneyFilter.value = '';
        if (taskStatusFilter) taskStatusFilter.value = '';
        if (assignedPlaceFilter) assignedPlaceFilter.value = '';
        if (deadlineFilter) deadlineFilter.value = '';
        
        filterTasks();
    }
    
    // Make functions global for HTML onclick handlers
    window.filterTasks = filterTasks;
    window.resetFilters = resetFilters;
    
    // Event listeners for filters
    if (searchInput) {
        searchInput.addEventListener('input', filterTasks);
    }
    
    if (moneyFilter) {
        moneyFilter.addEventListener('input', filterTasks);
    }
    
    if (taskStatusFilter) {
        taskStatusFilter.addEventListener('change', filterTasks);
    }
    
    if (assignedPlaceFilter) {
        assignedPlaceFilter.addEventListener('input', filterTasks);
    }
    
    if (deadlineFilter) {
        deadlineFilter.addEventListener('change', filterTasks);
    }
    
    // Initialize filters on page load
    filterTasks();
});
//------------------------------------------------------------------------//
