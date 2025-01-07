function createVercount() {
    let postPublish = document.getElementById('postPublish');
    if (postPublish){
        postPublish.insertAdjacentHTML('beforebegin','<div id="vercount_container_page_pv" style="display:none;float:left;margin-top:8px;font-size:small;">👁<span id="vercount_value_page_pv"></span></div>');
    }
    let runday = document.getElementById('runday');
    runday.insertAdjacentHTML('afterend', '<span id="vercount_container_site_pv" style="display:none">总浏览量<span id="vercount_value_site_pv"></span>次 • </span>');
}

document.addEventListener("DOMContentLoaded", function() {
    createVercount();
    let element = document.createElement('script');
    element.src = 'https://vercount.one/js';
    document.head.appendChild(element);
});