document.addEventListener('DOMContentLoaded', () => {
  const links = document.querySelectorAll('.links-list a');

  links.forEach((link) => {
    link.addEventListener('mouseenter', () => {
      link.style.color = '#50fa7b';
    });
    link.addEventListener('mouseleave', () => {
      link.style.color = '';
    });
  });

  const hero = document.querySelector('.hero-card');
  window.addEventListener('scroll', () => {
    const offset = window.scrollY * 0.03;
    hero.style.transform = `translateY(${offset}px)`;
  });
});
