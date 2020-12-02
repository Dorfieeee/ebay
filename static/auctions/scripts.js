class Carousel {
	constructor(carousel) {
		this.carousel = carousel;
		this.slider = carousel.querySelector('.slider');
		this.card = carousel.querySelector('.card');
		this.offset = 0;
	}

	slideLeft = () => {
		let maxOffset = (this.slider.offsetWidth - this.carousel.offsetWidth);
		let _offset = this.offset -
		(this.card.offsetWidth + getComputedStyle(this.card).marginRight.replace(/(px)$/, "") * 1);

		if (maxOffset < 0) {
			this.offset = 0;
		}
		else if (Math.abs(_offset) <= maxOffset) {
			this.offset = _offset;
		} else {
			this.offset = maxOffset * (-1);
		}

		this.slider.style.transform = `translateX(${this.offset}px)`;
	}		

	slideRight = () => {
		let _offset = this.offset + 
		(this.card.offsetWidth + getComputedStyle(this.card).marginRight.replace(/(px)$/, "") * 1);

		if (_offset < 0) {
			this.offset = _offset;
		} else {
			this.offset = 0;
		}

		this.slider.style.transform = `translateX(${this.offset}px)`;
	}

	watchResize = () => {
		let maxOffset = (this.slider.offsetWidth - this.carousel.offsetWidth);
		if (maxOffset < 0) {
			this.offset = 0;
		}
		else if (Math.abs(this.offset) > maxOffset) {
			this.offset = maxOffset * (-1);
		}
		this.slider.style.transform = `translateX(${this.offset}px)`;
	}

	init = () => {
		this.carousel.querySelector('.slider-btn.left').addEventListener('click', this.slideRight);
		this.carousel.querySelector('.slider-btn.right').addEventListener('click', this.slideLeft);
		window.addEventListener('resize', this.watchResize);
	}
};

document.querySelectorAll('.carousel').forEach(c => {
	let carousel = new Carousel(c);
	carousel.init();
});

const tgl = document.querySelector('.navbar-toggler');

const toggleSideMenu = () => {
	document.querySelector('.side-menu').classList.toggle('show');
	document.querySelector('.backdrop').classList.toggle('show');
};

tgl.addEventListener('click', toggleSideMenu)
document.querySelectorAll('.side-menu li').forEach(e => e.addEventListener('click', toggleSideMenu))