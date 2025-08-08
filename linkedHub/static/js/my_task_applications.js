// Tab switching functionality
        document.addEventListener('DOMContentLoaded', function() {
            const tabLinks = document.querySelectorAll('.tab-link');
            const tabContents = document.querySelectorAll('.tab-content');
            
            tabLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Remove active class from all tabs and links
                    tabLinks.forEach(l => l.classList.remove('active'));
                    tabContents.forEach(c => c.classList.remove('active'));
                    
                    // Add active class to clicked link
                    this.classList.add('active');
                    
                    // Show corresponding tab content
                    const targetTab = this.getAttribute('data-tab');
                    document.getElementById(targetTab).classList.add('active');
                });
            });
            
            // Real-time notification updates
            function updateNotificationBadge() {
                fetch('/api/notification-count/')  // You'll need to create this endpoint
                    .then(response => response.json())
                    .then(data => {
                        const notificationLink = document.getElementById('notificationLink');
                        const existingBadge = notificationLink.querySelector('.notification-badge, .notification-dot');
                        
                        // Remove existing badge/dot
                        if (existingBadge) {
                            existingBadge.remove();
                        }
                        
                        // Add new badge/dot if there are unread notifications
                        if (data.unread_count > 0) {
                            const badge = document.createElement('span');
                            badge.className = 'notification-badge';
                            badge.textContent = data.unread_count > 9 ? '9+' : data.unread_count;
                            notificationLink.appendChild(badge);
                        } else if (data.has_unread) {
                            const dot = document.createElement('span');
                            dot.className = 'notification-dot';
                            notificationLink.appendChild(dot);
                        }
                    })
                    .catch(error => console.log('Error fetching notification count:', error));
            }
            
            // Update notification badge every 30 seconds
            setInterval(updateNotificationBadge, 30000);
            
            // Mark notifications as read when clicking the bell icon
            document.getElementById('notificationLink').addEventListener('click', function() {
                // Optional: Mark notifications as read when clicked
                fetch('/api/mark-notifications-read/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/json',
                    },
                })
                .then(() => {
                    // Remove badge/dot immediately for better UX
                    const badge = this.querySelector('.notification-badge, .notification-dot');
                    if (badge) {
                        badge.remove();
                    }
                })
                .catch(error => console.log('Error marking notifications as read:', error));
            });
        });