function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}

toastr.options = {
    'closeButton': true,
    'debug': false,
    'newestOnTop': true,
    'progressBar': false,
    'positionClass': 'toast-top-right',
    'preventDuplicates': false,
    'showDuration': '1000',
    'hideDuration': '1000',
    'timeOut': '5000',
    'extendedTimeOut': '1000',
    'showEasing': 'swing',
    'hideEasing': 'linear',
    'showMethod': 'fadeIn',
    'hideMethod': 'fadeOut',
}

function alert_success(content){
    toastr.options.closeHtml = '<button class="closebtn"><i class="fa-solid fa-circle-xmark fa-lg"></i></i></button>';
    toastr.success('', content);
}

async function getRelationships(action){
    return await axios.get(`/api/users/friend?action=${action}`, {}, {
        headers: {
            "X-CSRF-TOKEN": getCookie("csrf_access_token")
        }
    })
}