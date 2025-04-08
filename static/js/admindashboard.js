/*=============== SHOW SIDEBAR ===============*/
const showSidebar = (toggleId, sidebarId, headerId, mainId) =>{
  const toggle = document.getElementById(toggleId),
        sidebar = document.getElementById(sidebarId),
        header = document.getElementById(headerId),
        main = document.getElementById(mainId)

  if(toggle && sidebar && header && main){
      toggle.addEventListener('click', ()=>{
          /* Show sidebar */
          sidebar.classList.toggle('show-sidebar')
          /* Add padding header */
          header.classList.toggle('left-pd')
          /* Add padding main */
          main.classList.toggle('left-pd')
      })
  }
}
showSidebar('header-toggle','sidebar', 'header', 'main')

/*=============== LINK ACTIVE ===============*/
const sidebarLink = document.querySelectorAll('.sidebar__list a')

function linkColor(){
   sidebarLink.forEach(l => l.classList.remove('active-link'))
   this.classList.add('active-link')
}

sidebarLink.forEach(l => l.addEventListener('click', linkColor))

/*=============== DARK LIGHT THEME ===============*/ 
const themeButton = document.getElementById('theme-button')
const darkTheme = 'dark-theme'
const iconTheme = 'ri-sun-fill'

// Previously selected topic (if user selected)
const selectedTheme = localStorage.getItem('selected-theme')
const selectedIcon = localStorage.getItem('selected-icon')

// We obtain the current theme that the interface has by validating the dark-theme class
const getCurrentTheme = () => document.body.classList.contains(darkTheme) ? 'dark' : 'light'
const getCurrentIcon = () => themeButton.classList.contains(iconTheme) ? 'ri-moon-clear-fill' : 'ri-sun-fill'

// We validate if the user previously chose a topic
if (selectedTheme) {
 // If the validation is fulfilled, we ask what the issue was to know if we activated or deactivated the dark
 document.body.classList[selectedTheme === 'dark' ? 'add' : 'remove'](darkTheme)
 themeButton.classList[selectedIcon === 'ri-moon-clear-fill' ? 'add' : 'remove'](iconTheme)
}

// Activate / deactivate the theme manually with the button
themeButton.addEventListener('click', () => {
   // Add or remove the dark / icon theme
   document.body.classList.toggle(darkTheme)
   themeButton.classList.toggle(iconTheme)
   // We save the theme and the current icon that the user chose
   localStorage.setItem('selected-theme', getCurrentTheme())
   localStorage.setItem('selected-icon', getCurrentIcon())
})

/*=============== Profile & notifications ===============*/
$(document).ready(function(){
  $(".profile .icon_wrap").click(function(){
    $(this).parent().toggleClass("active");
    $(".notifications").removeClass("active");
  });

  $(".notifications .icon_wrap").click(function(){
    $(this).parent().toggleClass("active");
     $(".profile").removeClass("active");
  });

});


/*=============== Image preview ===============*/
// DOM Elements
const dragArea = document.querySelector('.drag-area');
const dragText = document.querySelector('.drag-area header');
const browseBtn = document.getElementById('browseBtn');
const fileInput = document.querySelector('.drag-area input');
const image = document.querySelector('.drag-area img');
const closeBtn = document.querySelector('.close-btn');
const fileInfo = document.querySelector('.file-info');
const analyzeBtn = document.querySelector('.analyze-btn');
const uploadForm = document.getElementById('uploadForm');

// Global variables
let file;

// Click browse button to select file
browseBtn.onclick = () => {
    fileInput.click();
};

// Handle file selection
fileInput.addEventListener('change', function() {
    file = this.files[0];
    if (file) {
        image.style.height = '100%';
        showImage();
    }
});

// Drag over event
dragArea.addEventListener('dragover', (event) => {
    event.preventDefault();
    dragArea.classList.add('active');
    dragText.textContent = 'Release to Upload';
    image.style.height = '100%';
});

// Drag leave event
dragArea.addEventListener('dragleave', () => {
    dragArea.classList.remove('active');
    dragText.textContent = 'Drag & Drop';
    image.style.height = '80%';
});

// Drop event
dragArea.addEventListener('drop', (event) => {
    event.preventDefault();
    file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        fileInput.files = event.dataTransfer.files;
        showImage();
    } else {
        alert('Please upload an image file');
        dragArea.classList.remove('active');
        dragText.textContent = 'Drag & Drop';
    }
});

// Close button event
closeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    removeImage();
    image.style.height = '80%';
});

// Function to display the selected image
function showImage() {
    const fileReader = new FileReader();
    
    fileReader.onload = () => {
        const fileURL = fileReader.result;
        image.src = fileURL;
        dragArea.classList.add('active');
        closeBtn.style.display = 'flex';
        
        // Show file information
        const fileName = file.name;
        const fileSize = (file.size / 1024).toFixed(2) + ' KB';
        fileInfo.textContent = `${fileName} (${fileSize})`;
        fileInfo.style.display = 'block';
        
        // Show analyze button
        analyzeBtn.style.display = 'block';
    };
    
    fileReader.readAsDataURL(file);
}

// Function to remove the image
function removeImage() {
    image.src = '';
    dragArea.classList.remove('active');
    closeBtn.style.display = 'none';
    fileInfo.style.display = 'none';
    fileInput.value = '';
    file = null;
    dragText.textContent = 'Drag & Drop';
}