const slidePage = document.querySelector(".slide-page");
const nextBtnFirst = document.querySelector(".firstNext");
const prevBtnSec = document.querySelector(".prev-1");
const nextBtnSec = document.querySelector(".next-1");
const prevBtnThird = document.querySelector(".prev-2");
const nextBtnThird = document.querySelector(".next-2");
const prevBtnFourth = document.querySelector(".prev-3");
const submitBtn = document.querySelector(".submit");
const progressText = document.querySelectorAll(".step p");
const progressCheck = document.querySelectorAll(".step .check");
const bullet = document.querySelectorAll(".step .bullet");
let current = 1;

nextBtnFirst.addEventListener("click", function(event){
  event.preventDefault();
  slidePage.style.marginLeft = "-25%";
  bullet[current - 1].classList.add("active");
  progressCheck[current - 1].classList.add("active");
  progressText[current - 1].classList.add("active");
  current += 1;
});
nextBtnSec.addEventListener("click", function(event){
  event.preventDefault();
  slidePage.style.marginLeft = "-50%";
  bullet[current - 1].classList.add("active");
  progressCheck[current - 1].classList.add("active");
  progressText[current - 1].classList.add("active");
  current += 1;
});
nextBtnThird.addEventListener("click", function(event){
  event.preventDefault();
  slidePage.style.marginLeft = "-75%";
  bullet[current - 1].classList.add("active");
  progressCheck[current - 1].classList.add("active");
  progressText[current - 1].classList.add("active");
  current += 1;
});
submitBtn.addEventListener("click", function(){
  bullet[current - 1].classList.add("active");
  progressCheck[current - 1].classList.add("active");
  progressText[current - 1].classList.add("active");
  current += 1;
//   setTimeout(function(){
//     alert("Your Form Successfully Signed up");
//     location.reload();
//   },800);
});

prevBtnSec.addEventListener("click", function(event){
  event.preventDefault();
  slidePage.style.marginLeft = "0%";
  bullet[current - 2].classList.remove("active");
  progressCheck[current - 2].classList.remove("active");
  progressText[current - 2].classList.remove("active");
  current -= 1;
});
prevBtnThird.addEventListener("click", function(event){
  event.preventDefault();
  slidePage.style.marginLeft = "-25%";
  bullet[current - 2].classList.remove("active");
  progressCheck[current - 2].classList.remove("active");
  progressText[current - 2].classList.remove("active");
  current -= 1;
});
prevBtnFourth.addEventListener("click", function(event){
  event.preventDefault();
  slidePage.style.marginLeft = "-50%";
  bullet[current - 2].classList.remove("active");
  progressCheck[current - 2].classList.remove("active");
  progressText[current - 2].classList.remove("active");
  current -= 1;
});




// Popup configuration for different categories
const POPUP_TYPES = {
  success: {
      icon: `<svg width="60" height="60" viewBox="0 0 60 60">
          <circle cx="30" cy="30" r="29" fill="none" stroke="#4CAF50" stroke-width="2"/>
          <path d="M20 30 L28 38 L40 22" stroke="#4CAF50" stroke-width="3" fill="none"/>
      </svg>`,
      title: 'Success!',
      titleColor: '#4CAF50',
      buttonColor: '#4CAF50'
  },
  error: {
      icon: `<svg width="60" height="60" viewBox="0 0 60 60">
          <circle cx="30" cy="30" r="29" fill="none" stroke="#FF5252" stroke-width="2"/>
          <path d="M20 20 L40 40 M40 20 L20 40" stroke="#FF5252" stroke-width="3" fill="none"/>
      </svg>`,
      title: 'Error!',
      titleColor: '#FF5252',
      buttonColor: '#FF5252'
  },
  warning: {
      icon: `<svg width="60" height="60" viewBox="0 0 60 60">
          <circle cx="30" cy="30" r="29" fill="none" stroke="#FFA726" stroke-width="2"/>
          <path d="M30 15 L30 35 M30 40 L30 45" stroke="#FFA726" stroke-width="3" fill="none"/>
      </svg>`,
      title: 'Warning!',
      titleColor: '#FFA726',
      buttonColor: '#FFA726'
  },
  info: {
      icon: `<svg width="60" height="60" viewBox="0 0 60 60">
          <circle cx="30" cy="30" r="29" fill="none" stroke="#2196F3" stroke-width="2"/>
          <path d="M30 15 L30 20 M30 25 L30 45" stroke="#2196F3" stroke-width="3" fill="none"/>
      </svg>`,
      title: 'Information',
      titleColor: '#2196F3',
      buttonColor: '#2196F3'
  }
};

function showPopup(message, type ='success') {
  // Get popup configuration based on type
  const config = POPUP_TYPES[type] || POPUP_TYPES.info;
  
  const popup = document.createElement('div');
  popup.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: white;
      padding: 30px 40px;
      border-radius: 10px;
      box-shadow: 0 0 20px rgba(0,0,0,0.1);
      z-index: 1000;
      text-align: center;
      min-width: 300px;
      animation: fadeIn 0.3s ease-out;
  `;
  
  popup.innerHTML = `
      <style>
          @keyframes fadeIn {
              from { opacity: 0; transform: translate(-50%, -40%); }
              to { opacity: 1; transform: translate(-50%, -50%); }
          }
          .popup-button:hover {
              filter: brightness(90%);
          }
      </style>
      <div style="margin-bottom: 15px;">${config.icon}</div>
      <h2 style="margin: 15px 0; font-size: 24px; color: ${config.titleColor};">${config.title}</h2>
      <p style="margin: 10px 0 20px; color: #666; font-size: 16px;">${message}${config.title === 'Success!' ? '<br>Please log in to your account' : ''}</p>
      <button 
          class="popup-button"
          onclick="this.parentElement.remove()" 
          style="
              padding: 8px 40px;
              font-size: 16px;
              background: ${config.buttonColor};
              color: white;
              border: none;
              border-radius: 5px;
              cursor: pointer;
              transition: filter 0.3s;
          "
      >OK</button>
  `;
  
  document.body.appendChild(popup);
}

// Check for messages when the page loads
document.addEventListener('DOMContentLoaded', function() {
  if (window.message && window.messageType) {
      showPopup(window.message, window.messageType);
  } else if (window.message) {
      showPopup(window.message);
  }
});