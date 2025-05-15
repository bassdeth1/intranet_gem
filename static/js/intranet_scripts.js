// static/js/intranet_scripts.js
document.addEventListener('DOMContentLoaded', function () {
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');

    const themeToggleButton = document.getElementById('theme-toggle');
    const themeToggleIcon = themeToggleButton ? themeToggleButton.querySelector('i') : null;
    const notificationsButton = document.getElementById('notifications-button');
    const notificationsPanel = document.getElementById('notifications-panel');
    const currentYearSpan = document.getElementById('currentYear');

    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }
    
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    if (localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && prefersDark.matches)) {
        document.body.classList.add('dark-mode');
        if (themeToggleIcon) {
            themeToggleIcon.classList.remove('fa-moon');
            themeToggleIcon.classList.add('fa-sun');
        }
    }

    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
            if (themeToggleIcon) {
                themeToggleIcon.classList.toggle('fa-moon', !isDarkMode);
                themeToggleIcon.classList.toggle('fa-sun', isDarkMode);
            }
        });
    }
    
    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener('click', (event) => {
            event.stopPropagation(); 
            userMenu.classList.toggle('hidden');
            if (notificationsPanel && !notificationsPanel.classList.contains('hidden')) {
                notificationsPanel.classList.add('hidden');
            }
        });
    }

    if (notificationsButton && notificationsPanel) {
        notificationsButton.addEventListener('click', (event) => {
            event.stopPropagation(); 
            notificationsPanel.classList.toggle('hidden');
            if (userMenu && !userMenu.classList.contains('hidden')) {
                userMenu.classList.add('hidden');
            }
        });
    }

    document.addEventListener('click', (event) => {
        if (userMenuButton && userMenu && !userMenu.classList.contains('hidden') && !userMenuButton.contains(event.target) && !userMenu.contains(event.target)) {
            userMenu.classList.add('hidden');
        }
        if (notificationsButton && notificationsPanel && !notificationsPanel.classList.contains('hidden') && !notificationsButton.contains(event.target) && !notificationsPanel.contains(event.target)) {
            notificationsPanel.classList.add('hidden');
        }
    });

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('-translate-x-full'); 
        });
    }

    const navLinksForMobileSidebar = document.querySelectorAll('#sidebar .nav-link');
    navLinksForMobileSidebar.forEach(link => {
        link.addEventListener('click', (e) => {
            if (link.getAttribute('href') && link.getAttribute('href') !== '#') {
                if (sidebar && window.innerWidth < 768 && !sidebar.classList.contains('-translate-x-full')) { 
                    sidebar.classList.add('-translate-x-full');
                }
            }
            const notificationsNavLink = link.closest('#notifications-panel');
            if (notificationsNavLink && notificationsPanel && !notificationsPanel.classList.contains('hidden')) {
                 notificationsPanel.classList.add('hidden');
            }
        });
    });

    const fileUploadInput = document.getElementById('file-upload');
    const fileListDisplay = document.getElementById('file-list-display');
    if (fileUploadInput && fileListDisplay) {
        fileUploadInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                let fileNames = Array.from(this.files).map(file => file.name).join(', ');
                fileListDisplay.textContent = 'Archivos seleccionados: ' + fileNames;
            } else { 
                fileListDisplay.textContent = ''; 
            }
        });
    }
});