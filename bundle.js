const container = document.querySelector(".container");
const allMenus = document.querySelectorAll(".menu");

// Hide menus on body click
document.body.addEventListener("click", () => {
  allMenus.forEach(menu => {
    if (menu.classList.contains("open")) {
      menu.classList.remove("open");
    }
  });
});

// Reset menus on resize
window.addEventListener("resize", () => {
  allMenus.forEach(menu => {
    menu.classList.remove("open");
  });
});

// Handle desktop menu
allMenus.forEach(menu => {
  const trigger = menu.querySelector(".menu-trigger");
  const dropdown = menu.querySelector(".menu-dropdown");

  trigger.addEventListener("click", e => {
    e.stopPropagation();

    if (menu.classList.contains("open")) {
      menu.classList.remove("open");
    } else {
      // Close all menus...
      allMenus.forEach(m => m.classList.remove("open"));
      // ...before opening the current one
      menu.classList.add("open");
    }

    if (
      dropdown.getBoundingClientRect().right >
      container.getBoundingClientRect().right
    ) {
      dropdown.style.left = "auto";
      dropdown.style.right = 0;
    }
  });

  dropdown.addEventListener("click", e => e.stopPropagation());
});
const themeDark = "theme--dark";
const themeLight = "theme--light";
const bodyClassList = document.body.classList;
const isSystemDark = window.matchMedia(
  "(prefers-color-scheme: dark)",
).matches;
const themeToggle = document.querySelector(".theme-toggle");
const preferTheme = "prefer-theme";

// Set theme from local storage
const localTheme = localStorage.getItem(preferTheme);
if (localTheme === themeDark) {
  bodyClassList.add(themeDark);
} else if (localTheme === themeLight) {
  bodyClassList.remove(themeDark);
} else if (isSystemDark) {
  bodyClassList.add(themeDark);
}

// Set background for overscroll (or elastic scrolling in OSX)
function setBodyBackground() {
  const tc = document.querySelector(".theme-container");
  const cs = window.getComputedStyle(tc);
  document.body.style.background = cs.background;
}
setBodyBackground();

// Toggle theme on click
themeToggle.addEventListener("click", () => {
  if (bodyClassList.contains(themeDark)) {
    bodyClassList.remove(themeDark);
    localStorage.setItem(preferTheme, themeLight);
  } else {
    bodyClassList.add(themeDark);
    localStorage.setItem(preferTheme, themeDark);
  }
  setBodyBackground();
});
const hiTextBlock = document.querySelectorAll(".highlight-wrapper");

hiTextBlock.forEach(function (hiTextBlock) {
  const hiToolbar = hiTextBlock.querySelector(".highlight-toolbar");
  if (!hiToolbar) return;

  const hiText = hiTextBlock.querySelector(".highlight");
  if (!hiText) return;

  const copyButton = hiToolbar.querySelector(".js-btn-copy-code");
  if (!copyButton) return;

  copyButton.classList.remove("hide");

  /* Borrowed from adityatelange/hugo-PaperMod theme. */
  function copyingDone() {
    copyButton.innerHTML = "Copied!";
    setTimeout(() => {
      copyButton.innerHTML = "Copy";
    }, 2000);
  }

  /* copy code in pre > code blocks */
  copyButton.addEventListener("click", () => {
    // Fallback to selection and copy
    const range = document.createRange();
    range.selectNodeContents(hiText);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    try {
      document.execCommand("copy");
      copyingDone();
    } catch (e) {}
    selection.removeRange(range);
  });
});
/* TODO: Add print button */
