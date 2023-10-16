let searchOpen = document.querySelector('.search-box-btn');
let searchBox = document.querySelector('.search-box');
searchOpen.addEventListener('mouseover', function () {
    this.parentElement.classList.toggle('open'); //lấy ra đối tượng bên ngoài của seacrOpen
    document.getElementById("search-box-input").focus();//focust vào thẻ theo id
})
//bài học chỉ cách lấy element dựa vào this