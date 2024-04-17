document.addEventListener("DOMContentLoaded", function() {
  var loginButton = document.getElementById("loginButton");
  var loginButton2 = document.getElementById("loginButton2");
  var usernameInput = document.getElementById("usernameFormInput");
  var passwordInput = document.getElementById("passwordInput");

  function handleInputChange() {
    var username = usernameInput.value;
    var password = passwordInput.value;

    if (username.trim() === "" && password.trim() === "") {
        // window.location.href = "/cadastro";
        loginButton.style.display = "none";
        loginButton2.style.display = "block";
    } else {
        loginButton.innerHTML = "<b>LOGIN</b>";
        loginButton2.style.display = "none";
        loginButton.style.display = "block";
    }
}
usernameInput.addEventListener("input", handleInputChange);
passwordInput.addEventListener("input", handleInputChange);
handleInputChange();

});