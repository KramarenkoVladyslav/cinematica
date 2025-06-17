document.getElementById('burger-menu').addEventListener('click', function() {
    var filters = document.getElementById('filters');
    if (filters.style.display === 'none') {
        filters.style.display = 'block';
    } else {
        filters.style.display = 'none';
    }
});

document.querySelectorAll('#filters select').forEach(function(select) {
    select.addEventListener('change', function() {
        document.getElementById('filters').submit();
    });
});

document.getElementById('clear-filters').addEventListener('click', function() {
    document.querySelectorAll('#filters select').forEach(function(select) {
        select.selectedIndex = 0; 
    });
    document.getElementById('filters').submit(); 
});