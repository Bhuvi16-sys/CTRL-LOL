// ===========================================
// CTRL + LOL - CONFIGURATION
// ===========================================
const CONFIG = {
    brandText: "CTRL + LOL",
    tagline: "Humor \u2022 Creativity \u2022 Digital Expression",
    introDuration: 5000,
    particleCount: window.innerWidth < 768 ? 25 : 55,
    particleSpeed: 0.4
};

// ===========================================
// CUSTOM CURSOR
// ===========================================
class CustomCursor {
    constructor() {
        this.dot = document.querySelector('[data-cursor-dot]');
        this.outline = document.querySelector('[data-cursor-outline]');
        this.body = document.body;

        this.interactables = 'a, button, input, .team-card, .domain-card, .about-card, .timeline-content';

        if (this.dot && this.outline) {
            this.init();
        }
    }

    init() {
        let targetX = 0, targetY = 0;
        let currentX = 0, currentY = 0;
        let rafPending = false;

        const lerp = (a, b, t) => a + (b - a) * t;

        const updateOutline = () => {
            currentX = lerp(currentX, targetX, 0.15);
            currentY = lerp(currentY, targetY, 0.15);
            this.outline.style.left = currentX + 'px';
            this.outline.style.top = currentY + 'px';
            rafPending = false;
            if (Math.abs(currentX - targetX) > 0.5 || Math.abs(currentY - targetY) > 0.5) {
                rafPending = true;
                requestAnimationFrame(updateOutline);
            }
        };

        window.addEventListener('mousemove', (e) => {
            targetX = e.clientX;
            targetY = e.clientY;

            this.dot.style.left = targetX + 'px';
            this.dot.style.top = targetY + 'px';

            if (!rafPending) {
                rafPending = true;
                requestAnimationFrame(updateOutline);
            }
        });

        document.querySelectorAll(this.interactables).forEach(el => {
            el.addEventListener('mouseenter', () => this.body.classList.add('hovered'));
            el.addEventListener('mouseleave', () => this.body.classList.remove('hovered'));
        });

        document.addEventListener('mouseout', (e) => {
            if (!e.relatedTarget) {
                this.dot.style.opacity = '0';
                this.outline.style.opacity = '0';
            }
        });

        document.addEventListener('mouseover', (e) => {
            this.dot.style.opacity = '1';
            this.outline.style.opacity = '1';
        });
    }
}

// ===========================================
// 3D MEME-VERSE PARTICLE SYSTEM
// ===========================================
class ParticleSystem {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        // The vocabulary of the meme-verse
        this.memeVocabulary = ['😂', '💀', '🤡', '🔥', '🚀', 'L+Ratio', '404', 'LOL', 'BRUH', 'CTRL', '👀', '💩', 'POV', 'Git Push', 'SegFault'];
        this.resize();
        this.init();

        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.cx = this.canvas.width / 2;
        this.cy = this.canvas.height / 2;
    }

    init() {
        // Create 100 floating meme elements
        for (let i = 0; i < CONFIG.particleCount; i++) {
            this.particles.push(this.createParticle(true));
        }
    }

    createParticle(randomZ = false) {
        return {
            x: (Math.random() - 0.5) * this.canvas.width * 2, // Spread wide
            y: (Math.random() - 0.5) * this.canvas.height * 2,
            z: randomZ ? Math.random() * 2000 : 2000, // Start far away
            text: this.memeVocabulary[Math.floor(Math.random() * this.memeVocabulary.length)],
            color: this.getRandomColor(),
            speed: 5 + Math.random() * 10
        };
    }

    getRandomColor() {
        // Stats O'Locked Palette: cyan, orange, silver, white
        const colors = ['#00C8FF', '#38D9FF', '#FF6B1A', '#C0C8D8', '#FFFFFF', '#0080CC'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    update() {
        this.particles.forEach(p => {
            // Move particle towards the screen (decrease Z)
            p.z -= p.speed;

            // If it passes the screen, reset it to the back
            if (p.z <= 1) {
                Object.assign(p, this.createParticle());
            }
        });
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // No per-frame sort – skip Painter's Algorithm (negligible visual diff, big perf gain)
        const focalLength = 300;
        const W = this.canvas.width;
        const H = this.canvas.height;

        for (let i = 0; i < this.particles.length; i++) {
            const p = this.particles[i];
            const scale = focalLength / (focalLength + p.z);
            const x2d = this.cx + p.x * scale;
            const y2d = this.cy + p.y * scale;

            if (x2d < -50 || x2d > W + 50 || y2d < -50 || y2d > H + 50) continue;

            const alpha = Math.min(1, (2000 - p.z) / 1000);
            const fontSize = Math.max(10, 60 * scale) | 0; // bitwise floor

            this.ctx.globalAlpha = alpha;
            this.ctx.font = `700 ${fontSize}px Outfit,sans-serif`;
            this.ctx.fillStyle = p.color;
            this.ctx.fillText(p.text, x2d, y2d);
        }

        this.ctx.globalAlpha = 1;
    }

    animate() {
        this.update();
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
}

// ===========================================
// TEXT ANIMATOR
// ===========================================
class TextAnimator {
    constructor(element, text, speed = 60) {
        this.element = element;
        this.text = text;
        this.speed = speed;
        this.currentIndex = 0;
    }

    async animate() {
        return new Promise(resolve => {
            const interval = setInterval(() => {
                if (this.currentIndex < this.text.length) {
                    this.element.textContent += this.text[this.currentIndex];
                    this.currentIndex++;
                } else {
                    clearInterval(interval);
                    resolve();
                }
            }, this.speed);
        });
    }
}

// ===========================================
// PROGRESS BAR
// ===========================================
class ProgressBar {
    constructor(fillElement, textElement) {
        this.fillElement = fillElement;
        this.textElement = textElement;
        this.progress = 0;
    }

    update(percentage) {
        this.progress = Math.min(percentage, 100);
        this.fillElement.style.width = `${this.progress}%`;
        this.textElement.textContent = `${Math.floor(this.progress)}%`;
    }

    async animateTo(target, duration) {
        const start = this.progress;
        const distance = target - start;
        const startTime = Date.now();

        return new Promise(resolve => {
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);

                const easeOut = 1 - Math.pow(1 - progress, 3);
                const current = start + (distance * easeOut);

                this.update(current);

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            };
            animate();
        });
    }
}

// ===========================================
// SLOT MACHINE ANIMATOR
// ===========================================
class LockAnimator {
    constructor() {
        this.tumblers = [
            document.getElementById('tumbler-1'),
            document.getElementById('tumbler-2'),
            document.getElementById('tumbler-3')
        ];
        this.finalCode = ['L', 'O', 'L'];
        this.intervals = [];
    }

    async start() {
        // Start spinning all tumblers
        this.tumblers.forEach((tumbler, index) => {
            this.spinTumbler(tumbler, index);
        });

        // Stop them one by one
        await this.delay(1200);
        this.stopTumbler(0);

        await this.delay(600);
        this.stopTumbler(1);

        await this.delay(600);
        this.stopTumbler(2);
    }

    spinTumbler(element, index) {
        // Use emojis for the spinning animation
        const chars = ['😂', '💀', '🤡', '🔥', '🚀', '👀', '💩', '✨', '⚡️', '👾'];
        const spinColors = ['#00C8FF', '#38D9FF', '#FF6B1A', '#C0C8D8'];
        const interval = setInterval(() => {
            element.textContent = chars[Math.floor(Math.random() * chars.length)];
            element.style.color = spinColors[Math.floor(Math.random() * spinColors.length)];
        }, 50);
        this.intervals[index] = interval;
    }

    stopTumbler(index) {
        clearInterval(this.intervals[index]);
        const element = this.tumblers[index];
        element.textContent = this.finalCode[index];
        element.style.color = '#FF6B1A'; // Orange for the final letter

        element.parentElement.classList.add('unlocked');

        // Bounce effect
        element.parentElement.animate([
            { transform: 'scale(1)' },
            { transform: 'scale(1.5)' },
            { transform: 'scale(1)' }
        ], { duration: 300 });
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// ===========================================
// INTRO SEQUENCE MANAGER
// ===========================================
class IntroSequence {
    constructor() {
        this.introContainer = document.getElementById('intro-container');
        this.mainContent = document.getElementById('main-content');
        this.solText = document.getElementById('sol-text');
        this.brandTextElement = document.getElementById('brand-text');
        this.taglineElement = document.getElementById('tagline');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');

        this.progressBar = new ProgressBar(this.progressFill, this.progressText);
        this.lockAnimator = new LockAnimator();
    }

    async start() {
        await this.delay(500);
        this.animateSOL(); // Text glitch

        await this.delay(500);
        this.lockAnimator.start(); // Slot machine start

        await this.delay(300);
        const brandAnimator = new TextAnimator(this.brandTextElement, CONFIG.brandText, 60);
        await brandAnimator.animate();

        await this.delay(300);
        const taglineAnimator = new TextAnimator(this.taglineElement, CONFIG.tagline, 30);
        await taglineAnimator.animate();

        await this.delay(200);
        await this.progressBar.animateTo(100, 2200);

        await this.delay(600);
        this.fadeOutIntro();
    }

    animateSOL() {
        const text = this.solText;
        const original = "LOL";
        const chars = '01#@';
        let iterations = 0;

        const interval = setInterval(() => {
            text.textContent = text.textContent
                .split('')
                .map((char, index) => {
                    if (index < iterations) {
                        return original[index];
                    }
                    return chars[Math.floor(Math.random() * chars.length)];
                })
                .join('');

            iterations += 1 / 3;

            if (iterations >= original.length) {
                clearInterval(interval);
                text.textContent = original;
            }
        }, 50);
    }

    fadeOutIntro() {
        this.introContainer.classList.add('fade-out');
        setTimeout(() => {
            this.introContainer.classList.add('hidden');
            this.mainContent.classList.add('visible');
            document.body.style.overflow = 'auto';
            initMainPage();
        }, 1000);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// ===========================================
// MAIN PAGE INITIALIZATION
// ===========================================
function initMainPage() {
    initSmoothScroll();
    initScrollReveal();
    initCounters();
    initNavigation();
    initFloatingElements();

    if (window.innerWidth > 768) {
        new CustomCursor();
    }
}

function initNavigation() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
        document.querySelectorAll('.nav-menu a').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
            });
        });
    }
}

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = entry.target.dataset.delay || 0;
                setTimeout(() => {
                    entry.target.classList.add('aos-animate');
                }, delay);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('[data-aos]').forEach(el => observer.observe(el));
}

function initCounters() {
    const counters = document.querySelectorAll('.stat-number');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                entry.target.classList.add('counted');
                animateCounter(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
    const target = parseInt(element.dataset.count);
    const duration = 2000;
    const start = 0;
    const startTime = Date.now();

    const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (target * easeOut));
        element.textContent = current + (element.textContent.includes('+') ? '+' : '');
        if (progress < 1) requestAnimationFrame(animate);
    };
    animate();
}

function initFloatingElements() {
    const floatElements = document.querySelectorAll('.float-element');
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        floatElements.forEach(element => {
            const speed = parseFloat(element.dataset.speed) || 1;
            const yPos = -(scrolled * speed * 0.1);
            element.style.transform = `translateY(${yPos}px)`;
        });
    });
}

window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 80) {
        navbar.style.background = 'rgba(5, 13, 26, 0.97)';
    } else {
        navbar.style.background = 'rgba(5, 13, 26, 0.88)';
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const domainCards = document.querySelectorAll('.domain-card');
    domainCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
    document.body.style.overflow = 'hidden';

    const canvas = document.getElementById('particles');
    const particleSystem = new ParticleSystem(canvas);
    particleSystem.animate();

    const intro = new IntroSequence();
    intro.start();
});

console.log('%c🔓 CTRL + LOL ', 'font-size: 24px; font-weight: bold; color: #00C8FF;');
console.log('%cReady to enter the Meme-verse?', 'font-size: 14px; color: #FF6B1A;');
