(function () {
    var form = document.getElementById('filters');
    if (!form) return;

    var dropdowns = form.querySelectorAll('.filter-dropdown');

    function closeAll(except) {
        dropdowns.forEach(function (dd) {
            if (dd !== except) {
                dd.classList.remove('open');
                var panel = dd.querySelector('.filter-panel');
                if (panel) panel.style.display = 'none';
            }
        });
    }

    function openDropdown(dd) {
        dd.classList.add('open');
        var panel = dd.querySelector('.filter-panel');
        if (panel) panel.style.display = 'block';
    }

    function closeDropdown(dd) {
        dd.classList.remove('open');
        var panel = dd.querySelector('.filter-panel');
        if (panel) panel.style.display = 'none';
    }

    dropdowns.forEach(function (dd) {
        var trigger = dd.querySelector('.filter-trigger');
        var input   = dd.querySelector('input[type="hidden"]');
        var label   = dd.querySelector('.filter-label');
        var options = dd.querySelectorAll('.filter-option');

        trigger.addEventListener('click', function (e) {
            e.stopPropagation();
            var isOpen = dd.classList.contains('open');
            closeAll();
            if (!isOpen) openDropdown(dd);
        });

        options.forEach(function (opt) {
            opt.addEventListener('click', function () {
                var val  = opt.getAttribute('data-value');
                var text = opt.textContent.trim();

                input.value = val;
                label.textContent = text;

                if (val) {
                    label.classList.add('has-value');
                } else {
                    label.classList.remove('has-value');
                }

                dd.querySelectorAll('.filter-option').forEach(function (o) {
                    o.classList.remove('active');
                });
                opt.classList.add('active');

                closeDropdown(dd);
                form.requestSubmit();
            });
        });
    });

    document.addEventListener('click', function () {
        closeAll();
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeAll();
    });

    document.getElementById('burger-menu')?.addEventListener('click', function () {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    });

    document.getElementById('clear-filters')?.addEventListener('click', function () {
        dropdowns.forEach(function (dd) {
            var input = dd.querySelector('input[type="hidden"]');
            var label = dd.querySelector('.filter-label');

            input.value = '';
            label.textContent = 'All';
            label.classList.remove('has-value');

            dd.querySelectorAll('.filter-option').forEach(function (o) {
                o.classList.remove('active');
            });
            var firstOpt = dd.querySelector('.filter-option');
            if (firstOpt) firstOpt.classList.add('active');
        });
        closeAll();
        form.requestSubmit();
    });
})();
