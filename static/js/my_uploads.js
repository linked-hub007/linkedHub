// Delete material functionality
        document.addEventListener('DOMContentLoaded', function() {
            const deleteButtons = document.querySelectorAll('.delete-btn');
            const deleteForm = document.getElementById('deleteForm');
            const materialTitle = document.getElementById('materialTitle');
            
            deleteButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const materialId = this.getAttribute('data-material-id');
                    const materialRow = document.querySelector(`tr[data-material-id="${materialId}"]`);
                    const title = materialRow.querySelector('td:first-child a').textContent;
                    
                    // Set the form action URL
                    deleteForm.action = `/study-material/${materialId}/delete/`;
                    
                    // Set the material title in the modal
                    materialTitle.textContent = title;
                    
                    // Show the modal
                    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
                    modal.show();
                });
            });
            
            // Filter functionality
            const searchInput = document.getElementById('searchInput');
            const categoryFilter = document.getElementById('categoryFilter');
            const typeFilter = document.getElementById('typeFilter');
            
            function filterMaterials() {
                const searchTerm = searchInput.value.toLowerCase();
                const categoryValue = categoryFilter.value;
                const typeValue = typeFilter.value;
                
                document.querySelectorAll('tbody tr').forEach(row => {
                    const title = row.querySelector('td:first-child a').textContent.toLowerCase();
                    const category = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                    const type = row.querySelector('td:nth-child(3) span').textContent.toLowerCase();
                    
                    const matchesSearch = title.includes(searchTerm);
                    const matchesCategory = categoryValue === '' || category.includes(categoryFilter.options[categoryFilter.selectedIndex].text.toLowerCase());
                    const matchesType = typeValue === '' || type.includes(typeFilter.options[typeFilter.selectedIndex].text.toLowerCase());
                    
                    if (matchesSearch && matchesCategory && matchesType) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
            
            searchInput.addEventListener('input', filterMaterials);
            categoryFilter.addEventListener('change', filterMaterials);
            typeFilter.addEventListener('change', filterMaterials);
        });