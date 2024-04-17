document.addEventListener("DOMContentLoaded", function() {
  var formButton = document.getElementById("formUploadButton");

  formButton.addEventListener("click", function() {
    var usernameForm = document.getElementById("usernameFormInput");
    var passwordForm = document.getElementById("passwordFormInput");
    var passwordConfirm = document.getElementById("passwordConfirmInput");
    var errorForm = document.getElementById("errorFormMessage");

    if (usernameForm.value === "" || passwordForm.value === "" || passwordConfirm.value === "") {
      errorForm.innerHTML = "Por favor, preencha todos os campos.";
    } else if (passwordForm.value !== passwordConfirm.value) {
      errorForm.innerHTML = "As senhas não coincidem, tente novamente.";
    } else if (passwordForm.value.length  < 6) {
      errorForm.innerHTML = "A senha deve ter no minimo 6 caracteres";
    } else {
      errorForm.innerHTML = ""; // Limpar mensagem de erro se as senhas coincidirem
      // Aqui você pode adicionar a lógica para enviar as informações para validaçao
      // depois retornar para o anterior
      alert("Usuário " + usernameForm.value + " cadastrado com sucesso!");
      // Limpar form
      usernameForm.value = "";
      passwordForm.value = "";
      passwordConfirm.value = "";
    }
  });
});


document.addEventListener('DOMContentLoaded', function() {
  const colorOptions = document.querySelectorAll('.color-option');

  colorOptions.forEach(function(colorOption) {
      colorOption.addEventListener('click', function() {
          const selectedColor = colorOption.style.backgroundColor;
          console.log('Cor selecionada:', selectedColor);

          colorOptions.forEach(function(option) {
              option.style.border = 'none';
          });
          colorOption.style.border = '3px solid #fefefe';

          // FALTA guardar essa info
      });
  });
});

function trackTimeOnPage() {
  var startTime = new Date().getTime(); // Tempo inicial

  setInterval(function() {
      var currentTime = new Date().getTime();
      var elapsedTimeInSeconds = Math.floor((currentTime - startTime) / 1000);

      // Calcula minutos e segundos
      var minutes = Math.floor(elapsedTimeInSeconds / 60);
      var seconds = elapsedTimeInSeconds % 60;

      // Atualiza o elemento com o tempo decorrido
      document.getElementById('clock').textContent = formatTime(minutes, seconds);
  }, 1000);
}

// Formata o tempo em MM:SS
function formatTime(minutes, seconds) {
  return pad(minutes) + ':' + pad(seconds);
}

// Adiciona um zero à esquerda se for necessário
function pad(number) {
  return (number < 10 ? '0' : '') + number;
}

// Inicia a função quando a página é carregada
window.onload = function () {
  trackTimeOnPage();
};


// chat buble
// document.addEventListener("DOMContentLoaded", function() {
//   var chatBubble = document.querySelector(".chat-bubble");

//   chatBubble.addEventListener("click", function() {
//     // Aqui você pode adicionar o código para exibir o chat
//     // Por exemplo, mostrar um elemento de chat que estava oculto
//     console.log("Bolha de chat clicada!");
//   });
// });

const chatBubble = document.getElementById("chatBubble");
const chatContent = document.getElementById("chatContent");
const expandButton = document.getElementById("expandButton");
const collapseButton = document.getElementById("collapseButton");

// Função para expandir a bolha
function expandChat() {
  chatBubble.classList.add("expanded");
  chatContent.classList.add("visible");
  expandButton.classList.add("hidden");
  collapseButton.classList.add("visible");
}

// Função para contrair a bolha
function collapseChat() {
  chatBubble.classList.remove("expanded");
  chatContent.classList.remove("visible");
  expandButton.classList.remove("hidden");
  collapseButton.classList.remove("visible");
}

// Adiciona evento de clique ao botão de expansão
expandButton.addEventListener("click", expandChat);

// Adiciona evento de clique à área de conteúdo para contrair a bolha (opcional)
collapseButton.addEventListener("click", collapseChat);