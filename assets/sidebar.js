console.log('Sidebar loaded');
var sidebar = document.getElementById('sidebar');
var sidebarOpen = document.getElementById('toggle-sidebar');
var sidebarClose = document.getElementById('close-sidebar');

sidebarOpen.addEventListener('click', e => {
    e.preventDefault();
    if (sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
    } else {
        sidebar.classList.add('open');
    }
});

sidebarClose.addEventListener('click', e => {
    e.preventDefault();
    sidebar.classList.remove('open');
});

sidebar.addEventListener('click', e => {
    e.preventDefault();
    sidebar.classList.remove('open');
});
